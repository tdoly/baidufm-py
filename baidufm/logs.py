#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: logs.py
Author: tdoly
"""

import consts
import logging


PATTERN = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'


def __configure_logger():
    # 创建logger
    logger = logging.getLogger("baidufm")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(consts.HOST_PATH + "/baidufm.log")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(PATTERN)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def fm_log(logger, msg, *args, **kwargs):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(msg, *args, **kwargs)


if consts.DEBUG:
    __configure_logger()