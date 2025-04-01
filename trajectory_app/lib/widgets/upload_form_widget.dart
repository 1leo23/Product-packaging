import 'package:flutter/material.dart';
import 'package:trajectory_app/cards/upload_form_card.dart';

class UploadFormWidget extends StatelessWidget {
  const UploadFormWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return const Align(
      alignment: Alignment.topCenter,
      child: Padding(
        padding: EdgeInsets.symmetric(horizontal: 18, vertical: 20),
        child: Column(children: [UploadFormCard()]),
      ),
    );
  }
}
