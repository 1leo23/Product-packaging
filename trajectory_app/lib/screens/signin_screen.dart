import 'package:flutter/material.dart';
import 'package:trajectory_app/const/constant.dart';

class SigninScreen extends StatelessWidget {
  const SigninScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(color: cardBackgroundColor),
      child: Center(
        child: Container(
          width: 400,
          child: DefaultTabController(
            length: 2,
            child: Scaffold(
              backgroundColor: Colors.transparent,
              body: Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: 32.0,
                  vertical: 100.0,
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'Trajectory',
                      style: TextStyle(
                        //fontFamily: 'OldEnglish',
                        fontSize: 40,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    SizedBox(height: 20),
                    TabBar(
                      indicatorColor: Colors.tealAccent,
                      labelColor: Colors.white,
                      unselectedLabelColor: Colors.grey,
                      tabs: [Tab(text: '一般登入'), Tab(text: '醫師登入')],
                    ),
                    Expanded(
                      child: TabBarView(
                        children: [
                          _buildLoginForm(context, '/memberScreen'),
                          _buildLoginForm(context, '/managerScreen'),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLoginForm(BuildContext context, String route) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 24.0),
      child: Column(
        children: [
          TextField(
            cursorColor: Colors.tealAccent, // 修改游標顏色
            decoration: InputDecoration(
              hintText: '帳號',
              hintStyle: TextStyle(color: Colors.grey),
              filled: true,
              fillColor: cardBackgroundColor,

              border: OutlineInputBorder(
                borderSide: BorderSide(
                  color: Colors.tealAccent,
                  width: 2.0,
                ), // 修改點選時的邊框顏色
                borderRadius: BorderRadius.circular(8.0),
              ),
            ),
            style: TextStyle(color: Colors.white),
          ),
          SizedBox(height: 16),
          TextField(
            cursorColor: Colors.tealAccent, // 修改游標顏色
            obscureText: true,
            decoration: InputDecoration(
              hintText: '密碼',
              hintStyle: TextStyle(color: Colors.grey),
              filled: true,
              fillColor: cardBackgroundColor,
              border: OutlineInputBorder(
                borderSide: BorderSide(
                  color: Colors.tealAccent,
                  width: 2.0,
                ), // 修改點選時的邊框顏色
                borderRadius: BorderRadius.circular(8.0),
              ),
            ),
            style: TextStyle(color: Colors.white),
          ),
          SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: selectionColor,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8.0),
                ),
              ),
              onPressed: () {
                //登入事件
                Navigator.pushNamed(context, route);
              },
              child: Text(
                '登入',
                style: TextStyle(fontSize: 18, color: Colors.white),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
