import 'package:flutter/material.dart';
import 'package:trajectory_app/cards/custom_card.dart';
import 'package:trajectory_app/const/constant.dart';
import 'package:trajectory_app/data/member_data.dart';

class MemberCard extends StatelessWidget {
  final int index;
  final MemberData data;
  const MemberCard({super.key, required this.index, required this.data});
  @override
  Widget build(BuildContext context) {
    return CustomCard(
      width: 500,
      color: cardBackgroundColor, // 背景色
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
        child: Row(
          children: [
            // 頭像
            Container(
              width: 130, // 直徑 = 2 * radius
              height: 130,
              padding: EdgeInsets.all(5),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: selectionColor, // 邊框顏色
                  width: 2, // 邊框寬度
                ),
              ),
              child: CircleAvatar(
                radius: 64, // 內部頭像略小於容器，以顯示邊框
                backgroundColor: Colors.transparent,
                backgroundImage: AssetImage('/assets/images/avatar.png'),
              ),
            ),
            SizedBox(width: 16),
            // 文字資訊
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          data.memberList[index].name,
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),

                        ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: selectionColor,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(5.0),
                            ),
                            padding: EdgeInsets.symmetric(
                              vertical: 1.0,
                              horizontal: 16.0,
                            ),
                          ),
                          onPressed: () {
                            Navigator.pushNamed(context, '/memberScreen');
                          },
                          child: Text(
                            '選擇',
                            style: TextStyle(color: Colors.white, fontSize: 16),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Divider(
                    // 分隔線
                    color: selectionColor, // 直線顏色
                    thickness: 1.5, // 直線粗細
                  ),
                  _buildInfoRow('身份證字號', data.memberList[index].id),
                  _buildInfoRow(
                    '出生年月日',
                    '${data.memberList[index].yyyy}/${data.memberList[index].mm}/${data.memberList[index].dd}',
                  ),
                  _buildInfoRow('性別', data.memberList[index].sex),
                  _buildInfoRow('影像紀錄', '5'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 1, horizontal: 16.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              color: Colors.white54,
              fontWeight: FontWeight.w500,
              fontSize: 16,
            ),
          ),
          Text(
            value,
            style: TextStyle(
              color: Colors.white70,
              fontWeight: FontWeight.w500,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }
}
