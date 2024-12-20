## CasaDNS dynamic DNS service for smart homes

### Custom component for HACS in Home Assistant

![Static Badge](https://img.shields.io/badge/HACS-Custom-blue?style=flat)

This custom integration in HACS allows you to link your IP address to your own CasaDNS subdomain. If your IP address changes, the DNS is automatically updated so that your sudomein always continues to point to your smart home.

To use the integration in Home Assistant, you need to add the following configuration to your configuration.yaml file:

```
casadns:
  username: <YOUR USERNAME>
  secret: <YOUR PASSWORD>
```

Modify your username and secret in the above example. Your username is equal to your subdomain in _\<USERNAME\>_.casadns.eu.
