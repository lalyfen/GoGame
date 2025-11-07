"""
日志分析工具 - 用于分析应用访问日志
"""
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import os
from pathlib import Path

class LogAnalyzer:
    """日志分析器类"""

    def __init__(self, log_file_path):
        """
        初始化日志分析器

        Args:
            log_file_path (str): 日志文件路径
        """
        self.log_file_path = log_file_path
        self.access_patterns = {
            'access_log': re.compile(r'\[([\d\-:\s\.]+)\] ACCESS (\w+) \[([\w\.]+)\] (.+)'),
            'error_log': re.compile(r'\[([\d\-:\s\.]+)\] (\w+) \[([\w\.]+)\] ([\w\.\:]+) - (.+)'),
        }

    def analyze_access_logs(self, days=1):
        """
        分析访问日志

        Args:
            days (int): 分析最近几天的日志

        Returns:
            dict: 分析结果
        """
        if not os.path.exists(self.log_file_path):
            return {'error': f'日志文件不存在: {self.log_file_path}'}

        cutoff_date = datetime.now() - timedelta(days=days)
        stats = {
            'total_requests': 0,
            'users': defaultdict(int),
            'endpoints': defaultdict(int),
            'operations': defaultdict(int),
            'hourly_distribution': defaultdict(int),
            'errors': [],
            'recent_requests': []
        }

        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    # 尝试匹配访问日志格式
                    match = self.access_patterns['access_log'].match(line)
                    if match:
                        timestamp_str, level, logger_name, message = match.groups()

                        try:
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                            if timestamp < cutoff_date:
                                continue
                        except ValueError:
                            continue

                        stats['total_requests'] += 1

                        # 解析消息内容
                        self._parse_access_message(message, stats, timestamp)

        except Exception as e:
            stats['error'] = f'读取日志文件时出错: {str(e)}'

        return stats

    def _parse_access_message(self, message, stats, timestamp):
        """解析访问日志消息"""
        # 提取用户名
        user_match = re.search(r'用户: ([^,]+)', message)
        if user_match:
            username = user_match.group(1)
            stats['users'][username] += 1

        # 提取操作类型
        operation_match = re.search(r'^([^-]+)', message)
        if operation_match:
            operation = operation_match.group(1).strip()
            stats['operations'][operation] += 1

        # 提取端点信息（如果有）
        endpoint_match = re.search(r'游戏ID: ([^,\s]+)|交叉点ID: ([^,\s]+)', message)
        if endpoint_match:
            endpoint = endpoint_match.group(1) or endpoint_match.group(2)
            stats['endpoints'][endpoint] += 1

        # 按小时统计
        hour = timestamp.hour
        stats['hourly_distribution'][hour] += 1

        # 记录最近的请求
        if len(stats['recent_requests']) < 10:
            stats['recent_requests'].append({
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'message': message
            })

    def get_user_activity_summary(self, days=7):
        """获取用户活动摘要"""
        stats = self.analyze_access_logs(days)
        if 'error' in stats:
            return stats

        # 排序用户和操作
        top_users = sorted(stats['users'].items(), key=lambda x: x[1], reverse=True)[:10]
        top_operations = sorted(stats['operations'].items(), key=lambda x: x[1], reverse=True)

        return {
            'period': f'最近{days}天',
            'total_requests': stats['total_requests'],
            'unique_users': len(stats['users']),
            'top_users': top_users,
            'top_operations': top_operations,
            'hourly_peak': max(stats['hourly_distribution'].items(), key=lambda x: x[1]) if stats['hourly_distribution'] else None,
            'recent_requests': stats['recent_requests'][:5]
        }

    def generate_report(self, days=1, output_file=None):
        """生成日志报告"""
        stats = self.analyze_access_logs(days)
        if 'error' in stats:
            return f"生成报告失败: {stats['error']}"

        report = f"""
访问日志分析报告
================
分析时间范围: 最近{days}天
总请求数: {stats['total_requests']}
活跃用户数: {len(stats['users'])}

热门操作Top 10:
{self._format_counter(stats['operations'], 10)}

活跃用户Top 10:
{self._format_counter(stats['users'], 10)}

每小时请求分布:
{self._format_counter(stats['hourly_distribution'], 24)}

最近请求记录:
{self._format_recent_requests(stats['recent_requests'])}
        """

        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                return f"报告已保存到: {output_file}"
            except Exception as e:
                return f"保存报告失败: {str(e)}"

        return report

    def _format_counter(self, counter_dict, limit):
        """格式化计数器数据"""
        if not counter_dict:
            return "无数据"

        sorted_items = sorted(counter_dict.items(), key=lambda x: x[1], reverse=True)[:limit]
        return '\n'.join([f"  {item[0]}: {item[1]}次" for item in sorted_items])

    def _format_recent_requests(self, requests):
        """格式化最近请求"""
        if not requests:
            return "无最近请求"

        return '\n'.join([f"  {req['timestamp']} - {req['message']}" for req in requests[:5]])

def main():
    """主函数 - 演示日志分析功能"""
    BASE_DIR = Path(__file__).resolve().parent.parent
    log_file = os.path.join(BASE_DIR, 'logs', 'access.log')

    analyzer = LogAnalyzer(log_file)

    # 生成最近7天的报告
    report = analyzer.generate_report(days=7)
    print(report)

    # 获取用户活动摘要
    summary = analyzer.get_user_activity_summary(days=7)
    print(f"\n用户活动摘要: {summary}")

if __name__ == "__main__":
    main()