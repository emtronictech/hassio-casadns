# CasaDNS dynamic DNS service for smart homes

## Custom component for HACS in Home Assistant

![Static Badge](https://img.shields.io/badge/HACS-Custom-blue?style=flat)

This custom integration in HACS allows you to link your IP address to your own CasaDNS subdomain. If your IP address changes, the DNS is automatically updated so that your subdomain always continues to point to your smart home.

---

## Installation
### Installing via HACS _(recommended)_

- Install HACS if not already done.
- Add custom repository:
- In HACS > Integrations, add https://github.com/emtronictech/hassio_casadns
- Install Integration from HACS
- Restart Home Assistant

### Manual Installation

- Download this repository.
- Copy the **casadns** folder to custom_components/
- Restart Home Assistant

---

## Configuration

To use the integration in Home Assistant, you need to add the following configuration to your **configuration.yaml** file and change the required variables.

```
casadns:
  - name: <DOMAIN>.casadns.eu
    domain: <DOMAIN>
    token: <TOKEN>
```

Save the changes made in the configuration.yaml file and restart Home Assistant. 

_Change the variables DOMAIN and TOKEN in the above example! Your domain is equal to your subdomain in _\<DOMAIN\>_.casadns.eu._
