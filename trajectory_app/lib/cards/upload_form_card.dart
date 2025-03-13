import 'package:flutter/material.dart';
import 'package:trajectory_app/const/constant.dart';
import 'package:trajectory_app/cards/custom_card.dart';

class UploadFormCard extends StatelessWidget {
  const UploadFormCard({super.key});

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      width: 425,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 50, vertical: 10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '上傳影像',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            SizedBox(height: 16),
            _buildInputRow('身份證字號', '身份證字號', true),
            _buildInputRow('拍攝日期', '拍攝日期', true),
            _buildInputRow('上傳檔案', '上傳檔案 nii.gz', true),
            _buildInputRow('實際年齡', '實際年齡 (自動填入)', false),
            _buildInputRow('腦部年齡', '腦部年齡 (AI計算)', false),
            _buildInputRow('失智症風險', '失智症風險 (AI計算)', false),
            SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  flex: 3,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: selectionColor,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8.0),
                      ),
                      padding: EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 12,
                      ),
                    ),
                    onPressed: () {},
                    child: Text('AI計算', style: TextStyle(color: Colors.white)),
                  ),
                ),
                SizedBox(width: 20),
                Expanded(
                  flex: 2,
                  child: OutlinedButton(
                    style: OutlinedButton.styleFrom(
                      side: BorderSide(color: Colors.white),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8.0),
                      ),
                      padding: EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 12,
                      ),
                    ),
                    onPressed: () {},
                    child: Text('送出', style: TextStyle(color: Colors.white)),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

Widget _buildInputRow(String label, String hint, bool enabled) {
  return Padding(
    padding: const EdgeInsets.symmetric(vertical: 8.0),
    child: Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: TextStyle(color: Colors.white70, fontSize: 16)),
        SizedBox(
          height: 40,
          width: 200,
          child: TextField(
            enabled: enabled,
            style: TextStyle(color: Colors.white),
            decoration: InputDecoration(
              filled: true,
              fillColor:
                  enabled
                      ? Colors.transparent
                      : const Color.fromARGB(255, 55, 56, 74),
              hintText: hint,
              hintStyle: TextStyle(color: Colors.white54),
              border: OutlineInputBorder(
                borderSide: BorderSide(color: Colors.red),
                borderRadius: BorderRadius.circular(8.0),
              ),
              focusedBorder: OutlineInputBorder(
                borderSide: BorderSide(color: Colors.white),
                borderRadius: BorderRadius.circular(8.0),
              ),
              contentPadding: EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 10,
              ),
            ),
          ),
        ),
      ],
    ),
  );
}
