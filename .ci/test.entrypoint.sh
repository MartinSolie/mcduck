/usr/sbin/sshd \
&& /etc/init.d/xinetd restart \
&& until /etc/init.d/xinetd status > /dev/null 2>&1; do sleep 1; done \
&& python3 -m unittest \
    tests.test_ssh_executor \
    tests.test_telnet_executor \
    tests.test_local_executor
