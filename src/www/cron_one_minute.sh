#!/bin/bash

( cd /opt/freevo/www; . ENV; python ./rec_interface.py ) >> /tmp/rec.log 2>&1
