import 'dart:convert';
import 'dart:developer';

import 'package:http/http.dart' as http;


class User {
  String firstName, lastName;
  String email;
  String token;
  bool active;

  User({
    required this.firstName, required this.lastName,
    required this.email,
    required this.token,
    required this.active
  });

  User.fromMap(Map obj):
    firstName = obj["first_name"] as String,
    lastName = obj["last_name"] as String,
    email = obj["email"] as String,
    token = obj["token"] as String,
    active = obj["active"] as bool;
}

class PIClient {
  final baseURI = 'http://localhost:8080/api';

  User? user;

  PIClient();

  Future<void> login({ required String email, required String password }) async {
    final response = await http.post(
      Uri.parse('$baseURI/auth/login'),
      body: jsonEncode({
        "email": email,
        "password": password
      }),
      headers: {
        'Content-Type': 'application/json; charset=utf-8'
      }
    );

    if (response.statusCode > 299) {
      throw Exception("Failed to login");
    }

    user = User.fromMap(jsonDecode(response.body));

    return Future.value();
  }

  void logout() {
    user = null;
  }

  bool isAuthenticated() {
    return user != null;
  }
}
