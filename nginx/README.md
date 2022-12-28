# Nginx
Instructions for installing / configuring nginx server for tgfp.us

## Notes:
* Cloudflare redirects all http to https
* I use Cloudflare to generate a client certificate

## Instructions:

### Web server:
* The web server is run under a portainer stack as `tgfp-web`
* included `docker-compose.yaml` file is a 'snippet' to be included in a portainer stack

### GoshDarnedServer config
* create a directory $TGFP_HOME/nginx/conf and $TGFP_HOME/nginx/cloudflare
* app.conf goes under $TGFP_HOME/nginx/conf

### Get Cloudflare Certs
* Instructions here: https://developers.cloudflare.com/ssl/origin-configuration/origin-ca
  * Go to: https://dash.cloudflare.com
  * Click on TGFP.US -> SSL/TLS -> Origin Server
  * Click on 'Create Certificate'
    * copy Origin Certificate and create file `origcert.pem`
    * copy Private Key and create file `privkey.pem`
  * cloudflare client certificates (origin / private) go under $TGFP_HOME/nginx/cloudflare
     * `origcert.pem` (client cert)
     * `privkey.pem` (private key)

### Cloudflare domain config
* SSL Encryption mode to "Full (strict)" and redirect all traffic to https
  * Go to: https://dash.cloudflare.com
  * Click on TGFP.US -> SSL/TLS -> Overview
  * Choose "Full (strict)"
  * Click on SSL/TLS -> Edge Certificates
  * scroll down - Choose "Always use HTTPS"


### Notes about `app.conf`
* Don't redirect http to https
* proxy_pass http://tgfp-web:8000
  * NOTE: This sends traffic to tgfp-web internally


### Notes about `docker-compose.yaml` and network routing
* nginx listens to port 443 for ssl connections (port 80 isn't necessary since cloudflare redirects for us)
* docker compose exposes 7443 and forwards to 443
* firewall rule redirects external requests to 443 to goshdarnedserver:7443

### Notes about debugging
If for some reason you need to run a script manually, you can do so from this project provided you have the following:
* pycharm
* doppler cli installed
* poetry virtual environment set up (using the `pyproject.toml` file in the root of this project)
* You can run the config from the installed run configurations