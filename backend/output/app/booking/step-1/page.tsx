"use client";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { DatePicker } from "@/components/ui/date-picker";
import { SendHorizonal } from "lucide-react";
import { useState } from "react";

export default function Home() {
  const [checkInDate, setCheckInDate] = useState<Date | undefined>(undefined);
  const [checkOutDate, setCheckOutDate] = useState<Date | undefined>(undefined);
  return (
    <div className="flex flex-col items-center py-2">
      <div className="w-full max-w-md">
        <Card className="text-gray-700 bg-gray-100">
          <CardHeader>
            <CardTitle>日付・人数を選択してください</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-4">
            <div className="flex flex-col items-center">
              <p>チェックイン</p>
              <DatePicker
                date={checkInDate}
                setDate={setCheckInDate}
                name="CheckInDate"
              />
            </div>
            <div className="flex flex-col items-center">
              <p>チェックアウト</p>
              <DatePicker
                date={checkOutDate}
                setDate={setCheckOutDate}
                name="CheckOutDate"
              />
            </div>
            <div className="flex items-center">
              <span className="mx-5 text-nowrap">人数</span>
              <Select>
                <SelectTrigger className="ring-0 border-0 shadow-none focus-visible:ring-0">
                  <SelectValue placeholder="2人" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">1人</SelectItem>
                  <SelectItem value="2">2人</SelectItem>
                  <SelectItem value="3">3人</SelectItem>
                  <SelectItem value="4">4人</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="col-span-2 flex justify-center">
              <Button className="bg-ctm-blue-500 hover:bg-ctm-blue-600 w-full md:w-auto">
                <SendHorizonal className="w-5 h-5 mr-2" />
                空室検索
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
