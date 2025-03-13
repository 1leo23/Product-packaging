import 'package:flutter/material.dart';
import 'package:trajectory_app/cards/member_card.dart';
import 'package:trajectory_app/data/member_data.dart';

class MemberListWidget extends StatefulWidget {
  const MemberListWidget({super.key});

  @override
  State<MemberListWidget> createState() => _MemberListWidgetState();
}

class _MemberListWidgetState extends State<MemberListWidget> {
  @override
  Widget build(BuildContext context) {
    final data = MemberData();
    return Align(
      alignment: Alignment.topCenter, // 設定內容向上對齊
      child: ListView.builder(
        shrinkWrap: true, // 限制 ListView 的大小
        itemCount: data.memberList.length,
        itemBuilder:
            (context, index) => Column(
              children: [
                MemberCard(data: data, index: index),
                SizedBox(height: 10), // 這裡控制間距，例如 10
              ],
            ),
      ),
    );
  }
}
