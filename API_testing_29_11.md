# Authentication: 
curl -i -X POST "http://91.99.113.101/Authentication/login" -H "Content-Type: application/json" -d "{\"userName\":\"fa_fa\",\"password\":\"Smaecs_BIM_2025\"}"

# Setting the Token in bash
TOKEN="<set token>"

# POST Create new projects: 
curl -X POST http://91.99.113.101/bcf/3.0/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "A233FBB2-3A3B-EFF4-C123-DE22ABC8414",
    "name": "Example project 2",
    "project_actions": []
  }'

curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "F445F4F2-4D02-4B2A-B612-5E456BEF9137",
    "name": "Demo Project with BCF Extensions",
    "project_actions": ["update", "createTopic", "createDocument"]
  }' \
  http://91.99.113.101/bcf/3.0/projects

# GET existing Project(s): 
curl -H "Authorization: Bearer $TOKEN" http://91.99.113.101/bcf/3.0/projects

curl -H "Authorization: Bearer $TOKEN" http://91.99.113.101/bcf/3.0/projects/<project_id>

// curl -H "Authorization: Bearer $TOKEN" http://91.99.113.101/bcf/3.0/projects/F445F4F2-4D02-4B2A-B612-5E456BEF9137 //

# GET Project Extensions
curl -H "Authorization: Bearer $TOKEN" http://91.99.113.101/bcf/3.0/projects/9C3A7F21-8B54-4E2C-A91D-DF2075B3F84A/extensions

# GET existing Topic(s)
curl -H "Authorization: Bearer $TOKEN" http://91.99.113.101/bcf/3.0/projects/<project_id>/topics

// curl -H "Authorization: Bearer $TOKEN"  http://91.99.113.101/bcf/3.0/projects/F445F4F2-4D02-4B2A-B612-5E456BEF9137/topics //

curl -H "Authorization: Bearer $TOKEN" http://91.99.113.101/bcf/3.0/projects/<project_id>/topics/<topic_guid>

// curl -H "Authorization: Bearer $TOKEN"  http://91.99.113.101/bcf/3.0/projects/F445F4F2-4D02-4B2A-B612-5E456BEF9137/topics/04C57D6B-22B9-4AAC-9F11-F69E50441F15 //

# POST Create topics
curl -X POST http://91.99.113.101/bcf/3.0/projects/<project_id>/topics \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic_type": "Clash",
    "topic_status": "open",
    "title": "Example topic 3",
    "priority": "high",
    "labels": [
      "Architecture",
      "Heating"
    ],
    "assigned_to": "harry.muster@example.com",
    "bim_snippet": {
      "snippet_type": "clash",
      "is_external": true,
      "reference": "https://example.com/bcf/1.0/ADFE23AA11BCFF444122BB",
      "reference_schema": "https://example.com/bcf/1.0/clash.xsd"
    }
  }'

# PUT Update Topic
curl -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic_type": "Clash",
    "topic_status": "open",
    "title": "Example topic 3 - Changed Title",
    "priority": "high",
    "labels": [
      "Architecture",
      "Heating"
    ],
    "assigned_to": "harry.muster@example.com",
    "bim_snippet": {
      "snippet_type": "clash",
      "is_external": true,
      "reference": "https://example.com/bcf/1.0/ADFE23AA11BCFF444122BB",
      "reference_schema": "https://example.com/bcf/1.0/clash.xsd"
    }
  }' \
  http://91.99.113.101/bcf/3.0/projects/<project_id>/topics/<topic_guid>

# DELETE Topic
curl -X DELETE \
  -H "Authorization: Bearer $TOKEN" \
  http://91.99.113.101/bcf/3.0/projects/<project_id>/topics/<topic_guid>

# POST Comments
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "will rework the heating model"
  }' \
  http://91.99.113.101/bcf/3.0/projects/<project_id>/topics/<topic_id>/comments


# GET Comments
curl -H "Authorization: Bearer $TOKEN" \
  http://91.99.113.101/bcf/3.0/projects/<project_id>/topics/<topic_id>/comments

// curl -H "Authorization: Bearer $TOKEN" \
  http://91.99.113.101/bcf/3.0/projects/F445F4F2-4D02-4B2A-B612-5E456BEF9137/topics/04C57D6B-22B9-4AAC-9F11-F69E50441F15/comments //

# GET specific Comment
curl -H "Authorization: Bearer $TOKEN" \
  http://91.99.113.101/bcf/3.0/projects/<project_id>/topics/<topic_id>/comments/<guid>

// curl -H "Authorization: Bearer $TOKEN" \
  http://91.99.113.101/bcf/3.0/projects/F445F4F2-4D02-4B2A-B612-5E456BEF9137/topics/04C57D6B-22B9-4AAC-9F11-F69E50441F15/comments/FF734F08-30CC-44E9-9BD7-B55275AD2135 //

# PUT Comment
curl -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"comment": "will rework the heating model, discard the old one and fix the ventilation"}' \
  http://91.99.113.101/bcf/3.0/projects/<project_id>/topics/<topic_id>/comments/<guid>

# GET Viewpoints
curl -H "Authorization: Bearer $TOKEN" \
  http://91.99.113.101/bcf/3.0/projects/<PROJECT_ID>/topics/<TOPIC_GUID>/viewpoints

// curl -H "Authorization: Bearer $TOKEN" \
  http://91.99.113.101/bcf/3.0/projects/F445F4F2-4D02-4B2A-B612-5E456BEF9137/topics/04C57D6B-22B9-4AAC-9F11-F69E50441F15/viewpoints //

# POST Viewpoints
### you need to create a json file like vp.json that contains the info
curl -X POST   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d @vp.json   http://91.99.113.101/bcf/3.0/projects/<PROJECT_ID>/topics/<TOPIC_GUID>/viewpoints

# GET Viewpoint Selection
curl -H "Authorization: Bearer $TOKEN" \
  http://91.99.113.101/bcf/3.0/projects/<PROJECT_ID>/topics/<TOPIC_GUID>/viewpoints/<guid>/selection
  
// curl -H "Authorization: Bearer $TOKEN" \
  http://91.99.113.101/bcf/3.0/projects/F445F4F2-4D02-4B2A-B612-5E456BEF9137/topics/04C57D6B-22B9-4AAC-9F11-F69E50441F15/viewpoints/05BE56CB-BA68-430B-A7A1-73FE83BD9F34/selection

# GET Viewpoint Visibility
curl -H "Authorization: Bearer $TOKEN" \
  http://91.99.113.101/bcf/3.0/projects/<PROJECT_ID>/topics/<TOPIC_GUID>/viewpoints/<guid>/visibiity

// curl -H "Authorization: Bearer $TOKEN" \
  http://91.99.113.101/bcf/3.0/projects/F445F4F2-4D02-4B2A-B612-5E456BEF9137/topics/04C57D6B-22B9-4AAC-9F11-F69E50441F15/viewpoints/05BE56CB-BA68-430B-A7A1-73FE83BD9F34/visibility

# GET Viewpoint Snapshot
curl -H "Authorization: Bearer $TOKEN" \
  http://91.99.113.101/bcf/3.0/projects/<PROJECT_ID>/topics/<TOPIC_GUID>/viewpoints/<guid>/snapshot

// curl -H "Authorization: Bearer $TOKEN" \
  http://91.99.113.101/bcf/3.0/projects/F445F4F2-4D02-4B2A-B612-5E456BEF9137/topics/04C57D6B-22B9-4AAC-9F11-F69E50441F15/viewpoints/C4A37E76-0BB6-46C5-9C51-B3DB43FE5C0D/snapshot //

### if you want to save or retrieve an image file
curl -H "Authorization: Bearer $TOKEN" \
  -o snapshot.png \
  http://91.99.113.101/bcf/3.0/projects/<PROJECT_ID>/topics/<TOPIC_GUID>/viewpoints/<guid>/snapshot

// curl -H "Authorization: Bearer $TOKEN" \
  -o <filename>.png \  
  http://91.99.113.101/bcf/3.0/projects/F445F4F2-4D02-4B2A-B612-5E456BEF9137/topics/04C57D6B-22B9-4AAC-9F11-F69E50441F15/viewpoints/C4A37E76-0BB6-46C5-9C51-B3DB43FE5C0D/snapshot //

# GET Documents References
curl -H "Authorization: Bearer $TOKEN"   http://91.99.113.101/bcf/3.0/projects/<PROJECT_ID>/topics/<TOPIC_GUID>/document_references

// curl -H "Authorization: Bearer $TOKEN"   http://91.99.113.101/bcf/3.0/projects/F445F4F2-4D02-4B2A-B612-5E456BEF9137/topics/04C57D6B-22B9-4AAC-9F11-F69E50441F15/document_references //

# POST Document References

## document guid
curl -X POST   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d '{                                                                                     
    "document_guid": "472ab37a-6122-448e-86fc-86503183b520",
    "description": "The building owners global design parameters for buildings."
  }'   "http://91.99.113.101/bcf/3.0/projects/F445F4F2-4D02-4B2A-B612-5E456BEF9137/topics/04C57D6B-22B9-4AAC-9F11-F69E50441F15/document_references"

## url
curl -X POST   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d '{                                                                                     
    "url": "http://example.com/files/LegalRequirements.pdf",
    "description": "The legal requirements for buildings."
  }'   "http://91.99.113.101/bcf/3.0/projects/F445F4F2-4D02-4B2A-B612-5E456BEF9137/topics/04C57D6B-22B9-4AAC-9F11-F69E50441F15/document_references"

# GET Document list
curl -H "Authorization: Bearer $TOKEN" \
  "http://91.99.113.101/bcf/3.0/projects/<PROJECT_ID>/documents"

// curl -H "Authorization: Bearer $TOKEN" \
  "http://91.99.113.101/bcf/3.0/projects/F445F4F2-4D02-4B2A-B612-5E456BEF9137/documents" //

# GET specific Document
curl -H "Authorization: Bearer $TOKEN" \
  -o downloaded_testdoc.txt \
  "http://91.99.113.101/bcf/3.0/projects/<PROJECT_ID>/documents/<guid>"

// curl -H "Authorization: Bearer $TOKEN" \
  -o downloaded_testdoc.txt \
  "http://91.99.113.101/bcf/3.0/projects/F445F4F2-4D02-4B2A-B612-5E456BEF9137/documents/472ab37a-6122-448e-86fc-86503183b520" //

# POST Document

curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@LegalRequirements.pdf" \
  "http://91.99.113.101/bcf/3.0/projects/<PROJECT_ID>/documents/<guid>"

// curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@LegalRequirements.pdf" \
  "http://91.99.113.101/bcf/3.0/projects/F445F4F2-4D02-4B2A-B612-5E456BEF9137/documents?guid=472ab37a-6122-448e-86fc-86503183b520" //