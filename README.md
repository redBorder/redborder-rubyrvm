# redborder-rubyrvm
# Trobleshoooting

## Problem:
When running `sudo make rpm`, curls to some domains cannot be resolved.

## Solution:
Edit `/etc/mock/default.cfg` as sudo and add the following line:
`config_opts['use_host_resolve'] = True`
In Rocky 9 systems the file been used can be different so, if exists, edit `/etc/mock/default.cfg.rpmnew`
