FROM traefik:v2.4.3

RUN mkdir -p /etc/traefik/acme
RUN touch /etc/traefik/acme/acme.json
RUN chmod 600 /etc/traefik/acme/acme.json

COPY ./compose/production/traefik/traefik.yml /etc/traefik
COPY ./compose/production/traefik/traefik.dynamic.yml /etc/traefik