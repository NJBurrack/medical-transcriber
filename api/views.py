from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import TreatmentRequestSerializer, ICDRequestSerializer
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@api_view(['POST'])
def get_treatment(request):
    serializer = TreatmentRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    description = serializer.validated_data['description']
    
    prompt = f"""Extract patient age and provide brief treatment recommendation.

Patient: {description}

Format:
Age: [age in years]
Treatment: [2-3 sentence treatment plan only]"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You provide concise medical recommendations. Keep responses brief."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=150
        )
        
        ai_response = response.choices[0].message.content
        
        lines = ai_response.split('\n')
        age_line = "Not specified"
        treatment_text = ai_response
        
        for i, line in enumerate(lines):
            if "age:" in line.lower():
                age_line = line.split(':', 1)[1].strip()
            if "treatment:" in line.lower():
                treatment_text = '\n'.join(lines[i:]).replace('Treatment:', '').strip()
                break
        
        return Response({
            "response": {
                "age": f"Patient Age: {age_line}",
                "treatment": f"Recommended Treatment:\n{treatment_text}"
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def get_icd_codes(request):
    serializer = ICDRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    treatment = serializer.validated_data['treatment']
    
    
    prompt = f"""You must return ONLY the ICD-10 code. No explanation. No sentences. Just the code.

Treatment: {treatment}

Return only the code (example: J30.9)"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You return only ICD-10 codes. Never explain. Only return the code like 'J30.9'."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=10
        )
        
        icd_code = response.choices[0].message.content.strip()
        
        return Response({
            "treatment": treatment,
            "code": icd_code
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
