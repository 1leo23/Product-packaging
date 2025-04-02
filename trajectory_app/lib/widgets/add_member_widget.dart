import 'package:flutter/material.dart';
import 'package:trajectory_app/cards/add_member_card.dart';
import 'package:trajectory_app/models/member_model.dart';

class AddMemberWidget extends StatelessWidget {
  const AddMemberWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.topCenter,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 20),
        child: Container(child: Column(children: [const AddMemberCard()])),
      ),
    );
  }
}
