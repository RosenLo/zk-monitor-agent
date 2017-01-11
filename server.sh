#!/bin/bash

WORK_HOME="/opt/zk-monitor-agent"
VENV_HOME="$WORK_HOME/.venv"


source $VENV_HOME/bin/activate

case $1 in
    start) $VENV_HOME/bin/python $WORK_HOME/zk-monitor-agent start
        ;;
    stop) $VENV_HOME/bin/python $WORK_HOME/zk-monitor-agent stop
        ;;
    restart) $VENV_HOME/bin/python $WORK_HOME/zk-monitor-agent restart
        ;;
    *) $VENV_HOME/bin/python $WORK_HOME/zk-monitor-agent
        ;;
esac


