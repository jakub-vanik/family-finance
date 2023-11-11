FROM debian
RUN apt-get update && apt-get -y install cron git python3 python3-pip wget
RUN pip3 --no-cache-dir install Flask
RUN adduser --disabled-password --gecos "User" user
RUN mkdir /mnt/data && chmod 0777 /mnt/data
ADD --chown=root:root cron.d /etc/cron.d
ADD --chown=user:user famfin /home/user/famfin
CMD ["cron", "-f"]
