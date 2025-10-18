##下载俄罗斯的 IP 段列表wget -O ru.zone https://www.ipdeny.com/ipblocks/data/countries/ru.zone
#与block_russia_ip.sh脚本放同一个文件夹下

#运行脚本
#chmod +x block_russia_ip.sh
#sudo ./block_russia_ip.sh

#!/bin/bash
# 定义 IP 列表文件
RU_IP_LIST="ru.zone"

# 检查 UFW 是否已启用
if ! sudo ufw status | grep -q "Status: active"; then
    echo "UFW 未启用。请先启用 UFW 并允许必要的服务（例如 SSH）。"
    echo "示例: sudo ufw allow ssh"
    echo "         sudo ufw enable"
    exit 1
fi

# 检查 IP 列表文件是否存在
if [ ! -f "$RU_IP_LIST" ]; then
    echo "错误：找不到 IP 列表文件 '$RU_IP_LIST'。"
    echo "请运行 'wget -O ru.zone https://www.ipdeny.com/ipblocks/data/countries/ru.zone' 下载文件。"
    exit 1
fi

echo "正在从 '$RU_IP_LIST' 读取 IP 段并添加到 UFW 拒绝规则..."

# 计数器
COUNT=0

# 逐行读取 IP 段，并添加 UFW 拒绝规则
while IFS= read -r ip_range; do
    # 忽略空行和注释行
    if [[ -n "$ip_range" && ! "$ip_range" =~ ^# ]]; then
        # 注意：这里直接添加了拒绝规则。UFW 会按优先级处理。
        # 通常，显式的拒绝规则会优先于允许规则。
        # 但是，为了安全起见，强烈建议将更具体的允许规则放在拒绝整个范围之前。
        # 或者，您可以将拒绝规则放在 UFW 的 'before' 链中，但通过脚本直接管理更简单。
        echo "添加规则: sudo ufw deny from $ip_range"
        sudo ufw deny from "$ip_range"
        ((COUNT++))
    fi
done < "$RU_IP_LIST"

echo "共添加了 $COUNT 条 UFW 拒绝规则。"
echo "UFW 状态更新后可能需要一些时间来加载所有规则。"
sudo ufw status | head -n 20 # 显示前20条规则，因为列表可能非常长
