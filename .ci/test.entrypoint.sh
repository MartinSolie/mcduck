/usr/sbin/sshd \
&& /etc/init.d/xinetd restart \
&& sleep 2 \
&& python3 -m unittest \
    tests.test_ssh_executor \
    tests.test_telnet_executor \
    tests.test_local_executor

