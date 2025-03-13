import 'package:flutter/material.dart';
import 'package:trajectory_app/const/constant.dart';
import 'package:trajectory_app/widgets/add_member_widget.dart';
import 'package:trajectory_app/widgets/profile_widget.dart';
import 'package:trajectory_app/widgets/reports_widget.dart';
import 'package:trajectory_app/widgets/side_menu_widget.dart';

class MainScreen extends StatelessWidget {
  const MainScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: _appBar(),
      body: SafeArea(
        child: _buildPage(
          SideMenuWidget(type: 'member'),
          AddMemberWidget(),
          ProfileWidget(type: 'member'),
        ),
      ),
    );
  }
}

/*
醫師-上傳影像
_buildPage(
          SideMenuWidget(type: 'manager'),
          UploadFormWidget(),
          ProfileWidget(type: 'member'),
 ),

醫師-新增成員
_buildPage(
          SideMenuWidget(type: 'manager'),
          AddMemberWidget(),
          ProfileWidget(type: 'member'),
 ),

成員-腦部影像分析
_buildPage(
          SideMenuWidget(type: 'member'),
          ReportsWidget(),
          ProfileWidget(type: 'member'),
 ),
*/
Row _buildPage(
  SideMenuWidget sideMenuWidget,
  Widget mainWidget,
  ProfileWidget profileWidget,
) {
  return Row(
    children: [
      // Expanded (彈性布局)，通常用於Row和Col，使用flex分配空間比例，flex總和為12
      Expanded(flex: 2, child: SizedBox(child: sideMenuWidget)),
      Expanded(flex: 9, child: SizedBox(child: mainWidget)),
      Expanded(flex: 3, child: SizedBox(child: profileWidget)),
    ],
  );
}

AppBar _appBar() {
  return AppBar(
    title: Padding(
      padding: const EdgeInsets.only(left: 25),
      child: Text(
        "Trajectory",
        style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
      ),
    ),
    backgroundColor: appBarColor,
  );
}
