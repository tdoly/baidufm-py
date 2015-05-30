BaiduFm
======

|demo 3|

Baidu Fm CLI python实现.

Home page : http://tdoly.github.io/baidufm-py/
Source code : https://github.com/tdoly/baidufm-py

Feature
-------

::

    1.随机播放Baidu FM音乐
    2.登录Baidu FM（显示验证码）
    3.快捷键操作（上，下选择切歌...）
    4.暂停/恢复 播放
    5.静音
    6.音量调节
    7.收藏/取消收藏 音乐
    8.音乐加入垃圾箱

Install
-------

::

    pip install baidufm

Require
-------

::

    # ubuntu
    sudo apt-get install mplayer

    # OSX
    brew install mplayer

Using
-----

::

    baidufm

Keymap
------
::

    q 退出
    l 登陆
    ENTER 播放选择的频道
    n 下一首歌(当前频道)
    k (↑) 上
    j (↓) 下
    g 顶部
    G 底部
    b 上一页
    f 下一页
    + 加音量
    - 减音量
    p (空格) 暂停
    m 静音
    r 随机音乐
    c 收藏（取消收藏）音乐
    d 音乐加入垃圾箱
    # 刷新界面

Changelog
---------

0.2.2 基本功能
0.2.3 添加验证码显示功能，修复程序BUG

|demo 2|

License
-------

MIT

.. |demo 1| image:: http://blog.tdoly.com/baidufm-py/images/1.png
   :target: https://github.com/tdoly/baidufm-py
.. |demo 2| image:: http://blog.tdoly.com/baidufm-py/images/2.png
   :target: https://github.com/tdoly/baidufm-py
.. |demo 3| image:: http://blog.tdoly.com/baidufm-py/images/3.png
   :target: https://github.com/tdoly/baidufm-py
