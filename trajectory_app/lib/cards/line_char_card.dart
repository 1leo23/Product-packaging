import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:trajectory_app/data/line_data.dart';
import 'package:trajectory_app/cards/custom_card.dart';

class LineChartCard extends StatelessWidget {
  const LineChartCard({super.key});

  @override
  Widget build(BuildContext context) {
    final data = LineData();
    return CustomCard(
      // 需要import
      child: Padding(
        padding: const EdgeInsets.only(left: 10, right: 15, top: 5, bottom: 5),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '腦齡變化趨勢',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.w500),
            ),
            const SizedBox(height: 20),
            AspectRatio(
              // 強制子，強制維持Widget長寬比
              aspectRatio: 16 / 6,
              child: LineChart(
                LineChartData(
                  lineTouchData: LineTouchData(
                    handleBuiltInTouches: true, // 啟用 內建的觸控回應，可以點擊折線圖查看數據點的詳細資訊。
                  ),
                  gridData: FlGridData(show: false),
                  titlesData: FlTitlesData(
                    rightTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    topTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: true),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: true),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
