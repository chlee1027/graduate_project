import React, { useEffect, useState } from "react";
import { View, Text, ScrollView, ActivityIndicator, TouchableOpacity, TextInput, Alert, Modal } from "react-native";
import { Stack, useRouter } from "expo-router";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";

export default function Profile() {
  const { userId, reset } = useUserStore();
  const router = useRouter();
  
  const [userData, setUserDetails] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [weeklyDetails, setWeeklyDetails] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState<any>({});

  const fetchData = async () => {
    try {
      const [userRes, statsRes, detailsRes] = await Promise.all([
        client.get(`/api/user/${userId}`),
        client.get(`/api/stats/${userId}/summary`),
        client.get(`/api/stats/${userId}/weekly-details`)
      ]);
      setUserDetails(userRes.data);
      setStats(statsRes.data);
      setWeeklyDetails(detailsRes.data);
      setEditForm({
        age: userRes.data.age.toString(),
        height_cm: userRes.data.height_cm.toString(),
        weight_kg: userRes.data.weight_kg.toString(),
        goal: userRes.data.goal,
        weekly_available_days: userRes.data.weekly_available_days
      });
    } catch (error) {
      console.error("Failed to fetch profile data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) fetchData();
  }, [userId]);

  const handleUpdateProfile = async () => {
    try {
      setLoading(true);
      const updatePayload = {
        age: parseInt(editForm.age),
        height_cm: parseFloat(editForm.height_cm),
        weight_kg: parseFloat(editForm.weight_kg),
        goal: editForm.goal,
        weekly_available_days: editForm.weekly_available_days
      };

      await client.put(`/api/user/${userId}`, updatePayload);
      Alert.alert("성공", "프로필이 업데이트되었습니다.");
      setIsEditing(false);
      fetchData();
    } catch (error) {
      console.error("Update failed:", error);
      Alert.alert("오류", "정보 수정에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    Alert.alert("로그아웃", "정말 로그아웃 하시겠어요?", [
      { text: "취소", style: "cancel" },
      { 
        text: "로그아웃", 
        style: "destructive", 
        onPress: () => {
          reset();
          router.replace("/");
        } 
      }
    ]);
  };

  if (loading && !userData) {
    return (
      <View className="flex-1 justify-center items-center bg-white">
        <ActivityIndicator size="large" color="#2563eb" />
      </View>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ 
        title: "마이페이지", 
        headerShown: true,
        headerStyle: { backgroundColor: '#2563eb' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: "900", fontSize: 18 },
        headerShadowVisible: false,
        headerLeft: () => (
          <TouchableOpacity 
            onPress={() => router.back()} 
            className="ml-3 w-10 h-10 items-center justify-center rounded-full active:opacity-60"
          >
            <Ionicons name="chevron-back" size={26} color="#fff" style={{ marginLeft: -3 }} />
          </TouchableOpacity>
        ),
        headerRight: () => (
          <TouchableOpacity 
            onPress={handleLogout} 
            className="mr-3 w-10 h-10 items-center justify-center rounded-full active:opacity-60"
          >
            <Ionicons name="log-out-outline" size={24} color="#fff" />
          </TouchableOpacity>
        )
      }} />

      <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
        <View className="p-6">
          {/* Profile Header */}
          <View className="items-center mb-8">
            <View className="w-24 h-24 bg-blue-100 rounded-full items-center justify-center mb-4">
              <Text className="text-4xl text-blue-600">👤</Text>
            </View>
            <Text className="text-2xl font-black text-gray-900">{userId?.split('_')[0] || "사용자"} 님</Text>
            <Text className="text-gray-400 font-bold text-xs uppercase mt-1">AI Fitness Coach Member</Text>
          </View>

          {/* Stats Section (Moved from Home) */}
          <View className="flex-row justify-between mb-8">
            <View className="bg-gray-50 w-[31%] p-4 rounded-[32px] border border-gray-100 items-center">
              <Text className="text-gray-400 text-[10px] font-bold uppercase mb-1">누적 시간</Text>
              <Text className="text-xl font-black text-gray-900">{stats?.total_workout_minutes || 0}분</Text>
            </View>
            <View className="bg-gray-50 w-[31%] p-4 rounded-[32px] border border-gray-100 items-center">
              <Text className="text-gray-400 text-[10px] font-bold uppercase mb-1">완료 세션</Text>
              <Text className="text-xl font-black text-gray-900">{stats?.total_completed_workouts || 0}회</Text>
            </View>
            <View className="bg-orange-50 w-[31%] p-4 rounded-[32px] border border-orange-100 items-center">
              <Text className="text-orange-400 text-[10px] font-bold uppercase mb-1">소모 칼로리</Text>
              <Text className="text-xl font-black text-orange-600">{stats?.total_calories || 0}kcal</Text>
            </View>
          </View>

          {/* User Info Section */}
          <View className="bg-white border border-gray-100 rounded-[40px] p-8 shadow-sm mb-8">
            <View className="flex-row justify-between items-center mb-6">
              <Text className="text-lg font-black text-gray-900">내 정보</Text>
              <TouchableOpacity onPress={() => setIsEditing(true)}>
                <Text className="text-blue-600 font-bold text-sm">수정하기</Text>
              </TouchableOpacity>
            </View>

            <View className="space-y-4">
              <View className="flex-row justify-between py-2 border-b border-gray-50">
                <Text className="text-gray-400 font-bold">나이</Text>
                <Text className="text-gray-900 font-black">{userData?.age}세</Text>
              </View>
              <View className="flex-row justify-between py-2 border-b border-gray-50">
                <Text className="text-gray-400 font-bold">신체 정보</Text>
                <Text className="text-gray-900 font-black">{userData?.height_cm}cm / {userData?.weight_kg}kg</Text>
              </View>
              <View className="flex-row justify-between py-2 border-b border-gray-50">
                <Text className="text-gray-400 font-bold">운동 목표</Text>
                <Text className="text-gray-900 font-black">
                  {userData?.goal === 'muscle_gain' ? '근성장' : 
                   userData?.goal === 'weight_loss' ? '체중 감량' : '건강 유지'}
                </Text>
              </View>
              <View className="flex-row justify-between py-2">
                <Text className="text-gray-400 font-bold">주간 목표</Text>
                <Text className="text-gray-900 font-black">{userData?.weekly_available_days}회</Text>
              </View>
            </View>
          </View>

          {/* Injuries Section */}
          <View className="bg-red-50 border border-red-100 rounded-[40px] p-8 mb-8">
            <Text className="text-lg font-black text-red-900 mb-4">현재 부상/주의 부위 ⚠️</Text>
            {userData?.injuries.length > 0 ? (
              <View className="flex-row flex-wrap">
                {userData.injuries.map((injury: string) => (
                  <View key={injury} className="bg-white px-4 py-2 rounded-full mr-2 mb-2 border border-red-200">
                    <Text className="text-red-600 font-bold text-xs">{injury}</Text>
                  </View>
                ))}
              </View>
            ) : (
              <Text className="text-red-400 text-xs font-bold">현재 등록된 부상 정보가 없습니다. 아주 건강하시네요!</Text>
            )}
          </View>

          {/* Exercise History Section (NEW) */}
          <View className="bg-white border border-gray-100 rounded-[40px] p-8 shadow-sm mb-8">
            <Text className="text-lg font-black text-gray-900 mb-6">최근 운동 기록 📜</Text>
            {weeklyDetails.length > 0 ? (
              <View className="space-y-4">
                {weeklyDetails.map((item, index) => (
                  <View key={item.log_id || index} className="flex-row items-center justify-between py-3 border-b border-gray-50">
                    <View className="flex-1">
                      <Text className="text-gray-900 font-black text-base">{item.plan_name}</Text>
                      <Text className="text-gray-400 text-[10px] font-bold">
                        {item.date} • {item.location === 'gym' ? '헬스장' : '집'}
                      </Text>
                    </View>
                    <View className="items-end">
                      <Text className="text-blue-600 font-black text-lg">{item.minutes}분</Text>
                      <Text className="text-gray-400 text-[8px] font-bold">{item.calories} kcal</Text>
                    </View>
                  </View>
                ))}
              </View>
            ) : (
              <View className="items-center py-4">
                <Text className="text-gray-400 font-bold text-xs text-center">아직 이번 주 운동 기록이 없네요.{"\n"}첫 운동을 시작해볼까요?</Text>
              </View>
            )}
          </View>
        </View>
      </ScrollView>

      {/* Edit Modal */}
      <Modal visible={isEditing} animationType="slide" transparent={true}>
        <View className="flex-1 justify-end bg-black/50">
          <View className="bg-white rounded-t-[48px] p-8 h-[80%]">
            <View className="flex-row justify-between items-center mb-8">
              <Text className="text-2xl font-black text-gray-900">정보 수정 ✏️</Text>
              <TouchableOpacity onPress={() => setIsEditing(false)}>
                <Ionicons name="close" size={28} color="#111827" />
              </TouchableOpacity>
            </View>

            <ScrollView showsVerticalScrollIndicator={false}>
              <View className="space-y-6">
                <View>
                  <Text className="text-gray-400 font-bold text-[10px] uppercase mb-2">몸무게 (kg)</Text>
                  <TextInput
                    value={editForm.weight_kg}
                    onChangeText={(text) => setEditForm({ ...editForm, weight_kg: text })}
                    keyboardType="numeric"
                    className="bg-gray-50 p-4 rounded-2xl font-black text-lg border border-gray-100"
                  />
                </View>

                <View>
                  <Text className="text-gray-400 font-bold text-[10px] uppercase mb-2">키 (cm)</Text>
                  <TextInput
                    value={editForm.height_cm}
                    onChangeText={(text) => setEditForm({ ...editForm, height_cm: text })}
                    keyboardType="numeric"
                    className="bg-gray-50 p-4 rounded-2xl font-black text-lg border border-gray-100"
                  />
                </View>

                <View>
                  <Text className="text-gray-400 font-bold text-[10px] uppercase mb-2">운동 목표</Text>
                  <View className="flex-row space-x-2">
                    {['muscle_gain', 'weight_loss', 'fitness'].map((g) => (
                      <TouchableOpacity
                        key={g}
                        onPress={() => setEditForm({ ...editForm, goal: g })}
                        className={`flex-1 p-3 rounded-xl border items-center ${
                          editForm.goal === g ? "bg-blue-600 border-blue-600" : "bg-white border-gray-200"
                        }`}
                      >
                        <Text className={`font-bold text-[10px] ${editForm.goal === g ? "text-white" : "text-gray-400"}`}>
                          {g === 'muscle_gain' ? '근성장' : g === 'weight_loss' ? '감량' : '건강'}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>

                <TouchableOpacity
                  onPress={handleUpdateProfile}
                  className="bg-blue-600 p-5 rounded-3xl items-center shadow-lg mt-8"
                >
                  <Text className="text-white font-black text-lg">저장하기</Text>
                </TouchableOpacity>
              </View>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}
