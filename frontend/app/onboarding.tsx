import React, { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, ScrollView, Alert, Modal, FlatList } from "react-native";
import { useRouter, Stack } from "expo-router";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { SafeAreaView } from "react-native-safe-area-context";

export default function Onboarding() {
  const router = useRouter();
  const { setUserId, setIsOnboarded } = useUserStore();

  const [isAgeModalVisible, setIsAgeModalVisible] = useState(false);
  const [isHeightModalVisible, setIsHeightModalVisible] = useState(false);
  const [isWeightModalVisible, setIsWeightModalVisible] = useState(false);

  const [form, setForm] = useState({
    user_id: "user_" + Math.random().toString(36).substr(2, 5),
    age: 25,
    sex: "male",
    height_cm: 175,
    weight_kg: 70,
    goal: "muscle_gain",
    experience_level: "beginner",
    injuries: [],
    weekly_available_days: 3,
    place_preference: "gym",
    equipment: ["dumbbell", "barbell"],
  });

  const handleOnboarding = async () => {
    try {
      const response = await client.post("/api/onboarding/", form);
      if (response.status === 200) {
        setUserId(form.user_id);
        setIsOnboarded(true);
        Alert.alert("완료", "온보딩이 성공적으로 완료되었습니다!");
        router.replace("/");
      }
    } catch (error) {
      console.error(error);
      Alert.alert("오류", "온보딩 중 문제가 발생했습니다.");
    }
  };

  const SelectionGroup = ({ label, options, current, onSelect, noMargin }: any) => (
    <View className={noMargin ? "" : "mb-6"}>
      <Text className="text-gray-700 font-bold mb-3">{label}</Text>
      <View className="flex-row flex-wrap">
        {options.map((opt: any) => (
          <TouchableOpacity
            key={opt.value}
            onPress={() => onSelect(opt.value)}
            className={`mr-2 mb-2 px-4 py-2 rounded-full border ${
              current === opt.value
                ? "bg-blue-600 border-blue-600"
                : "bg-white border-gray-300"
            }`}
          >
            <Text
              className={current === opt.value ? "text-white font-bold" : "text-gray-600"}
            >
              {opt.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  const ages = Array.from({ length: 51 }, (_, i) => i + 15);
  const heights = Array.from({ length: 81 }, (_, i) => i + 140);
  const weights = Array.from({ length: 111 }, (_, i) => i + 40);

  const VerticalPickerModal = ({ visible, onClose, data, selectedValue, onSelect, title, unit }: any) => (
    <Modal visible={visible} transparent={true} animationType="slide">
      <View className="flex-1 justify-end bg-black/50">
        <View className="bg-white rounded-t-3xl p-6 h-1/2">
          <View className="flex-row justify-between items-center mb-4">
            <Text className="text-xl font-bold text-gray-800">{title}</Text>
            <TouchableOpacity onPress={onClose}>
              <Text className="text-blue-600 font-bold">완료</Text>
            </TouchableOpacity>
          </View>
          <FlatList
            data={data}
            keyExtractor={(item) => item.toString()}
            renderItem={({ item }) => (
              <TouchableOpacity
                onPress={() => {
                  onSelect(item);
                  onClose();
                }}
                className={`p-4 items-center border-b border-gray-100 ${
                  selectedValue === item ? "bg-blue-50" : ""
                }`}
              >
                <Text className={`text-lg ${selectedValue === item ? "text-blue-600 font-bold" : "text-gray-600"}`}>
                  {item}
                </Text>
              </TouchableOpacity>
            )}
          />
        </View>
      </View>
    </Modal>
  );

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ title: "회원 정보 입력" }} />
      <ScrollView className="p-6">
        <Text className="text-2xl font-bold mb-2">당신을 알려주세요</Text>
        <Text className="text-gray-500 mb-8">AI가 당신에게 꼭 맞는 운동을 설계합니다.</Text>
        
        <View className="flex-row mb-6">
          <View className="flex-1 mr-2">
            <Text className="text-gray-700 font-bold mb-3">키 (cm)</Text>
            <TouchableOpacity
              onPress={() => setIsHeightModalVisible(true)}
              className="bg-gray-50 h-14 px-4 rounded-xl border border-gray-200 flex-row justify-between items-center"
            >
              <Text className="text-gray-700 text-base" style={{ includeFontPadding: false }}>{form.height_cm}</Text>
              <Text className="text-blue-600 font-bold text-xs">선택</Text>
            </TouchableOpacity>
          </View>

          <View className="flex-1 ml-2">
            <Text className="text-gray-700 font-bold mb-3">몸무게 (kg)</Text>
            <TouchableOpacity
              onPress={() => setIsWeightModalVisible(true)}
              className="bg-gray-50 h-14 px-4 rounded-xl border border-gray-200 flex-row justify-between items-center"
            >
              <Text className="text-gray-700 text-base" style={{ includeFontPadding: false }}>{form.weight_kg}</Text>
              <Text className="text-blue-600 font-bold text-xs">선택</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View className="flex-row mb-6">
          <View className="w-1/2 pr-2">
            <Text className="text-gray-700 font-bold mb-3">나이 (세)</Text>
            <TouchableOpacity
              onPress={() => setIsAgeModalVisible(true)}
              className="bg-gray-50 h-14 px-4 rounded-xl border border-gray-200 flex-row justify-between items-center"
            >
              <Text className="text-gray-700 text-base" style={{ includeFontPadding: false }}>{form.age}</Text>
              <Text className="text-blue-600 font-bold text-xs">변경</Text>
            </TouchableOpacity>
          </View>
        </View>

        <VerticalPickerModal
          visible={isAgeModalVisible}
          onClose={() => setIsAgeModalVisible(false)}
          data={ages}
          selectedValue={form.age}
          onSelect={(val: number) => setForm({ ...form, age: val })}
          title="나이 선택"
          unit="세"
        />

        <VerticalPickerModal
          visible={isHeightModalVisible}
          onClose={() => setIsHeightModalVisible(false)}
          data={heights}
          selectedValue={form.height_cm}
          onSelect={(val: number) => setForm({ ...form, height_cm: val })}
          title="키 선택"
          unit="cm"
        />

        <VerticalPickerModal
          visible={isWeightModalVisible}
          onClose={() => setIsWeightModalVisible(false)}
          data={weights}
          selectedValue={form.weight_kg}
          onSelect={(val: number) => setForm({ ...form, weight_kg: val })}
          title="몸무게 선택"
          unit="kg"
        />

        <SelectionGroup
          label="성별"
          options={[
            { label: "남성", value: "male" },
            { label: "여성", value: "female" },
          ]}
          current={form.sex}
          onSelect={(v: string) => setForm({ ...form, sex: v })}
        />

        <SelectionGroup
          label="운동 목표"
          options={[
            { label: "체중 감량", value: "weight_loss" },
            { label: "근력 증진", value: "muscle_gain" },
            { label: "건강 유지", value: "fitness" },
          ]}
          current={form.goal}
          onSelect={(v: string) => setForm({ ...form, goal: v })}
        />

        <SelectionGroup
          label="숙련도"
          options={[
            { label: "초보자", value: "beginner" },
            { label: "중급자", value: "intermediate" },
            { label: "상급자", value: "advanced" },
          ]}
          current={form.experience_level}
          onSelect={(v: string) => setForm({ ...form, experience_level: v })}
        />

        <SelectionGroup
          label="선호 장소"
          options={[
            { label: "집 (홈트)", value: "home" },
            { label: "헬스장", value: "gym" },
          ]}
          current={form.place_preference}
          onSelect={(v: string) => setForm({ ...form, place_preference: v })}
        />

        <TouchableOpacity
          className="bg-blue-600 p-5 rounded-2xl items-center mt-4 mb-10 shadow-lg shadow-blue-200"
          onPress={handleOnboarding}
        >
          <Text className="text-white font-bold text-xl">시작하기</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}
