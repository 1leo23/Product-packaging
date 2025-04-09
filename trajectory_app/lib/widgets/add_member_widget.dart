import 'package:flutter/material.dart';
import 'package:trajectory_app/cards/add_member_card.dart';

class AddMemberWidget extends StatefulWidget {
  final VoidCallback? onMemberAdded; // 為了更新醫生的成員數
  const AddMemberWidget({super.key, this.onMemberAdded});

  @override
  State<AddMemberWidget> createState() => _AddMemberWidgetState();
}

class _AddMemberWidgetState extends State<AddMemberWidget> {
  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.topCenter,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 20),
        child: Column(
          children: [AddMemberCard(onMemberAdded: widget.onMemberAdded)],
        ),
      ),
    );
  }
}
