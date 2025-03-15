import 'package:flutter/material.dart';
import 'package:trajectory_app/cards/brain_veiwer_card.dart';
import 'package:trajectory_app/cards/selet_record_card.dart';

class RecordsWidget extends StatelessWidget {
  const RecordsWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 20),
        child: Column(
          children: [
            SelectRecordCard(),
            SizedBox(height: 18),
            //BrainViewerCard(),
          ],
        ),
      ),
    );
  }
}
