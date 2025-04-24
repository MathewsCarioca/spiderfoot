FROM alpine:3.12.4 AS build
ARG REQUIREMENTS=requirements.txt
RUN apk add --no-cache gcc git curl python3 python3-dev py3-pip swig tinyxml-dev \
 python3-dev musl-dev openssl-dev libffi-dev libxslt-dev libxml2-dev jpeg-dev \
 openjpeg-dev zlib-dev cargo rust
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin":$PATH
COPY $REQUIREMENTS requirements.txt ./
RUN ls
RUN echo "$REQUIREMENTS"
RUN pip3 install -U pip
RUN pip3 install -r "$REQUIREMENTS"



FROM alpine:3.13.0
WORKDIR /home/spiderfoot
RUN echo "https://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
# Place database and logs outside installation directory
ENV SPIDERFOOT_DATA /var/lib/spiderfoot
ENV SPIDERFOOT_LOGS /var/lib/spiderfoot/log
ENV SPIDERFOOT_CACHE /var/lib/spiderfoot/cache

# Run everything as one command so that only one layer is created
RUN apk --update --no-cache add python3 musl openssl libxslt tinyxml libxml2 jpeg zlib openjpeg nmap nmap-scripts ruby ruby-bundler ruby-dev build-base git yaml-dev nano git musl-dev gcc musl-dev wget tar \
    && addgroup spiderfoot \
    && adduser -G spiderfoot -h /home/spiderfoot -s /sbin/nologin \
               -g "SpiderFoot User" -D spiderfoot \
    && rm -rf /var/cache/apk/* \
    && rm -rf /lib/apk/db \
    && rm -rf /root/.cache \
    && mkdir -p $SPIDERFOOT_DATA || true \
    && mkdir -p $SPIDERFOOT_LOGS || true \
    && mkdir -p $SPIDERFOOT_CACHE || true \
    && chown spiderfoot:spiderfoot $SPIDERFOOT_DATA \
    && chown spiderfoot:spiderfoot $SPIDERFOOT_LOGS \
    && chown spiderfoot:spiderfoot $SPIDERFOOT_CACHE 

# Clonar o WhatWeb diretamente do repositório
RUN git clone https://github.com/urbanadventurer/WhatWeb.git /opt/whatweb \
    && cd /opt/whatweb \
    && bundle install

RUN ln -s /opt/whatweb/whatweb /usr/local/bin/whatweb

# Nuclei
# Baixar e instalar Go 1.22.3
RUN wget -q https://go.dev/dl/go1.22.3.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.22.3.linux-amd64.tar.gz && \
    rm go1.22.3.linux-amd64.tar.gz

# Adicionar Go ao PATH
ENV PATH="/usr/local/go/bin:$PATH"

# Clonar e compilar Nuclei
RUN git clone --depth 1 https://github.com/projectdiscovery/nuclei.git /opt/nuclei && \
    cd /opt/nuclei/cmd/nuclei && \
    go build && \
    mv nuclei /usr/local/bin/


RUN mkdir -p /opt/nuclei-templates && \
    git clone https://github.com/projectdiscovery/nuclei-templates.git /opt/nuclei-templates && \
    nuclei -update-templates -t /opt/nuclei-templates

COPY . .
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY final.py /home/spiderfoot/final.py

USER root

EXPOSE 5001

# Run the application.
ENTRYPOINT ["/opt/venv/bin/python", "/home/spiderfoot/final.py"]
CMD ["/home/spiderfoot/final.py", "tail", "-f", "/dev/null"]
#CMD ["/bin/bash", "-c", "tail -f /dev/null"]
