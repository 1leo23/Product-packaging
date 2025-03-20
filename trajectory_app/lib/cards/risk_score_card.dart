import 'package:flutter/material.dart';
import 'package:flutter_icon_shadow/flutter_icon_shadow.dart';
import 'package:trajectory_app/cards/custom_card.dart';

class RiskScoreCard extends StatefulWidget {
  const RiskScoreCard({super.key});

  @override
  State<RiskScoreCard> createState() => _RiskScoreCard();
}

class _RiskScoreCard extends State<RiskScoreCard> {
  @override
  Widget build(BuildContext context) {
    return CustomCard(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '失智症風險',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 30),
              child: Stack(
                alignment: Alignment.topCenter,
                clipBehavior: Clip.none,
                children: [
                  // 風險區間背景條
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      _riskSegment(Colors.green, '低風險'),
                      _riskSegment(Colors.yellow, '輕度風險'),
                      _riskSegment(Colors.orange, '中度風險'),
                      _riskSegment(Colors.red, '高度風險'),
                    ],
                  ),

                  // 疊加風險指標圖示
                  _riskIndicatorIcon(34),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _riskIndicatorIcon(int riskScore) {
    final MAGIC_NUMBER = 2;
    final LEFT_FIEX = (riskScore - MAGIC_NUMBER).clamp(0, 100);
    final RIGHT_FIEX = (100 - MAGIC_NUMBER - riskScore).clamp(0, 100);
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Expanded(flex: LEFT_FIEX, child: Container()),
        Expanded(
          flex: 0,
          child: IconShadow(
            Icon(Icons.kitesurfing_outlined, size: 30),
            shadowColor: Colors.black,
            shadowOffset: Offset(2, 2),
          ),
        ),
        Expanded(flex: RIGHT_FIEX, child: Container()),
      ],
    );
  }
}

// 風險區間的顏色條
Widget _riskSegment(Color color, String label) {
  return Expanded(
    flex: 24,
    child: Column(
      children: [
        SizedBox(height: 20),
        Container(height: 16, color: color),
        SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    ),
  );
}
