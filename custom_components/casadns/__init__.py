"""CasaDNS - Dynamic DNS service for smart homes"""
import asyncio
from datetime import timedelta
import logging

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant.const import (
    CONF_USERNAME,
    CONF_SECRET,
    CONF_UPDATE_INTERVAL
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DEFAULT_INTERVAL = timedelta(minutes=15)

TIMEOUT = 30
HOST = "casadns.eu"

CASADNS_RESPONSE_ERRORS = {
    "Forbidden": "Invalid username password combination",
    "Unauthorized": "Invalid combination of username and secret",
    "Blocked": "Browser user agent not allowed or IP address blocked",
    "Abuse": "Username is blocked due to abuse",
}

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_SECRET): cv.string,
                vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_INTERVAL): vol.All(
                    cv.time_period, cv.positive_timedelta
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Initialize CasaDNS component"""
    conf = config[DOMAIN]
    username = conf.get(CONF_USERNAME).strip()
    secret = conf.get(CONF_SECRET).strip()
    update_interval = conf.get(CONF_UPDATE_INTERVAL)

    session = async_get_clientsession(hass)

    result = await _update_dns(session, username, secret)

    if not result:
        return False

    async def update_dns_interval(now):
        """Update the DNS record"""
        await _update_dns(session, username, secret)

    async_track_time_interval(hass, update_dns_interval, interval)

    return True


async def _update_dns(session, username, secret):
    try:
        url = f"https://casadns.eu/dns/?username={username}&secret={secret}"
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