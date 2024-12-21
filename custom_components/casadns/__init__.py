"""CasaDNS - Dynamic DNS service for smart homes"""
import asyncio
from datetime import timedelta
import logging
import aiohttp
import async_timeout
import socket
import voluptuous as vol

from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType
from homeassistant.util.location import async_detect_location_info
from homeassistant.util.network import is_ipv4_address

_LOGGER = logging.getLogger(__name__)

DEFAULT_INTERVAL = timedelta(minutes=15)

DOMAIN = "casadns"
TIMEOUT = 30
HOST = "casadns.eu"

CASADNS_RESPONSE_ERRORS = {
    "Forbidden": "Invalid username password combination",
    "Unauthorized": "Invalid combination of username and password",
    "Blocked": "Browser user agent not allowed or IP address blocked",
    "Abuse": "Username is blocked due to abuse",
}

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_INTERVAL): vol.All(
                    cv.time_period, cv.positive_timedelta
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Initialize CasaDNS component"""
    session = async_get_clientsession(hass, family=socket.AF_INET)
    location_info = await async_detect_location_info(session)

    if not location_info or not is_ipv4_address(location_info.ip):
        _LOGGER.warning("Could not get external IPv4 address for updating DNS %s.%s", username, HOST)
        return False

    for casadns_idx, conf in enumerate(config[DOMAIN]):
        config_name = conf.get(CONF_NAME).strip()
        username = conf.get(CONF_USERNAME).strip()
        password = conf.get(CONF_PASSWORD).strip()
        interval = conf.get(CONF_SCAN_INTERVAL)

        if config_name is None:
            config_name = f"CasaDNS_entry_{casadns_idx}"
            _LOGGER.debug("# Found no name for CasaDNS entry, generated a unique name: %s", config_name)

        _LOGGER.debug("%s # Setting up CasaDNS entry with config:\n %s", config_name, conf)

        updateDnsResult = await _update_dns(session, username, password)

        if not updateDnsResult:
            continue

        async def update_dns_interval(now):
            await _update_dns(session, username, password)

        async_track_time_interval(hass, update_dns_interval, interval)

async def _update_dns(session, username, password):
    try:
        url = f"https://casadns.eu/dns/?username={username}&password={password}"
        async with async_timeout.timeout(TIMEOUT):
            resp = await session.get(url)
            body = await resp.text()

            if body.startswith("OK"):
                _LOGGER.info("Updating DNS for %s.%s", username, HOST)
                return True

            _LOGGER.warning("Updating DNS failed: %s.%s => %s", username, HOST, CASADNS_RESPONSE_ERRORS[body.strip()])

    except aiohttp.ClientError:
        _LOGGER.warning("Can't connect to CasaDNS server: %s.%s", username, HOST)

    except asyncio.TimeoutError:
        _LOGGER.warning("CasaDNS server timeout: %s.%s", username, HOST)

    return False
