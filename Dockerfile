FROM debian
RUN apt-get update && apt-get -y install cron git python3 python3-flask python3-werkzeug wget
RUN useradd -m user && mkdir /mnt/data && chmod 0777 /mnt/data
ADD --chown=root:root cron.d /etc/cron.d
ADD --chown=user:user famfin /home/user/famfin
CMD ["cron", "-f"]
