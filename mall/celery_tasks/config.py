
# 用于保存celery配置信息
# 中间人的设置选择redis的１４号库
broker_url = "redis://127.0.0.1/14"
# redis的１５号库　用于保存结果
result_backend="redis://127.0.0.1/15"