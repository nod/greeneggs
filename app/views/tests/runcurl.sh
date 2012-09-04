#!/bin/sh
curl -F secret=changethis --form "checkin=<./xx" 127.0.0.1:9988/api/fs/push
