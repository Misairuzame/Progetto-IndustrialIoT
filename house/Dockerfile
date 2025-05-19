FROM python:3.13-slim

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y tzdata
RUN ln -snf /usr/share/zoneinfo/Europe/Rome /etc/localtime

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN apt-get install -y mosquitto tmux

# Filebeat
ARG STACK_VERSION
ENV STACK_VERSION=${STACK_VERSION}

RUN apt-get install -y wget apt-transport-https gpg
RUN wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
RUN MAJOR_VERSION="$(echo $STACK_VERSION | cut -f1 -d'.')"; \
    echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/${MAJOR_VERSION}.x/apt stable main" \
    | tee /etc/apt/sources.list.d/elastic-"${MAJOR_VERSION}".x.list
RUN apt-get update && apt-get install -y filebeat=${STACK_VERSION}
# Versione senza uso della variabile STACK_VERSION:
#RUN echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/9.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-9.x.list
#RUN apt-get update && apt-get install -y filebeat

COPY filebeat/filebeat.yml /etc/filebeat/filebeat.yml

# Make tmux pretty
RUN apt-get install -y git
RUN mkdir -p ~/.config/tmux/plugins/catppuccin
RUN git clone -b v2.1.3 https://github.com/catppuccin/tmux.git ~/.config/tmux/plugins/catppuccin/tmux
RUN cat <<EOF >> ~/.tmux.conf
# Pick a softer palette.
set -g @catppuccin_flavor 'frappe'

run ~/.config/tmux/plugins/catppuccin/tmux/catppuccin.tmux

# Make the status line more pleasant.
set -g status-left ""
set -g status-right '#[fg=#{@thm_crust},bg=#{@thm_teal}] session: #S '

# Ensure that everything on the right side of the status line
# is included.
set -g status-right-length 100
EOF

COPY . .

CMD ["bash", "house-new.sh"]
