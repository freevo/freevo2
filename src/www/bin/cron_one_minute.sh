#!/bin/bash

( cd /opt/freevo/src/www; . ./bin/ENV; python ./rec_interface.py ) >> /tmp/rec.log 2>&1
