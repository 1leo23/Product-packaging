import 'package:flutter/material.dart';
import 'package:trajectory_app/cards/line_char_card.dart';
import 'package:trajectory_app/cards/risk_score_card.dart';

class ReportsWidget extends StatelessWidget {
  const ReportsWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 20),
        child: Column(
          children: [RiskScoreCard(), SizedBox(height: 18), LineChartCard()],
        ),
      ),
    );
  }
}
