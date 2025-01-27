import 'dart:developer';

import 'package:flutter/material.dart';

import 'package:file_picker/file_picker.dart';

import 'package:pi/PIAPI/client.dart';
import 'package:pi/PIAPI/campaing_api_extension.dart';


class CampaignsPage extends StatefulWidget {
  final PIClient apiClient;

  const CampaignsPage({ super.key, required this.apiClient });

  @override
  State<CampaignsPage> createState() => _CampaignsPageState();
}

class _CampaignsPageState extends State<CampaignsPage> {

  @override
  Widget build(BuildContext context) {
    return FutureBuilder(
      future: widget.apiClient.fetchStatusUploadedCampaign(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Expanded(child: Column(children: [
            Spacer(flex: 99),
            CircularProgressIndicator(),
            Spacer(flex: 2),
            Text("Checando se há campanhas sendo carregada..."),
            Spacer(flex: 99),
          ]));
        } else {
          if (!snapshot.hasData) {
            return buildUpload();
          }

          final data = snapshot.data!;

          if (data["status"] == "LOADING") {
            WidgetsBinding.instance.addPostFrameCallback((_) async {
              await Future.delayed(const Duration(seconds: 2)).then((value) => setState(() => ()));
            });
            return const Expanded(child: Column(children: [
              Spacer(flex: 99),
              CircularProgressIndicator(),
              Spacer(flex: 2),
              Text("Existe uma campanha sendo carregada..."),
              Spacer(flex: 99),
            ]));
          } else {
            List<String> failedLeads = (data["failed_leads"] as List<dynamic>).cast<String>();

            if (failedLeads.isNotEmpty) {
              WidgetsBinding.instance.addPostFrameCallback((_) {
                showDialog(
                  context: context,
                  builder: (BuildContext context) {
                    return AlertDialog(
                      title: const Text("Não foi possivel recuperar os seguintes usuários."),
                      content: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: failedLeads.map((lead) => ListTile(leading: const Icon(Icons.error, color: Colors.red), title: Text(lead)))
                                            .toList()
                      ),
                      actions: [ TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text("Fechar")) ],
                    );
                  }
                );
              });
            }
          }

          return buildUpload();
        }
      }
    );
  }

  Widget buildUpload() {
    return Expanded(child: Center( // Centers the content both vertically and horizontally
      child: Column(
        mainAxisSize: MainAxisSize.min, // Ensures the column only takes the space it needs
        children: [
          TextButton(
            onPressed: () async {
              FilePickerResult? result = await FilePicker.platform.pickFiles();

              if (result != null) {
                widget.apiClient.uploadCampaign(result.files.single.bytes!);
                setState(() => ());
              }
            },
            child: const FractionallySizedBox(
              alignment: Alignment.center,
              widthFactor: 0.25,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.file_open),
                  VerticalDivider(width: 1, color: Colors.transparent),
                  Text("Carregar campanha"),
                ],
              ),
            )
          ),
        ],
      ),
    ));
  }
}
