FROM python:3-stretch

COPY . /app
WORKDIR /app
RUN true \
    && apt-get update \
    && apt-get install -y openssh-server xinetd telnetd \
    && echo 'telnet stream tcp wait telnetd /usr/sbin/tcpd /usr/sbin/in.telnetd' >> /etc/inetd.conf \
    && mkdir /var/run/sshd \
    && useradd -ms /bin/bash admin \
    && echo 'admin:sIcretandsecYre' | chpasswd \
    && touch /home/admin/hello.world \
    && sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd \
    && mkdir /etc/testing \
    && cp requirements.txt /etc/testing/requirements.txt \
    && pip3 install -r /etc/testing/requirements.txt \
    && chmod +x /app/.ci/test.entrypoint.sh \
    && true
COPY ./.ci/telnet.test.config /etc/xinetd.d/telnet

ENTRYPOINT /app/.ci/test.entrypoint.sh

