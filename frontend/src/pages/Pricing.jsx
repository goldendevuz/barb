import React from 'react';
import { Card, Button, Badge } from 'antd';
import { CheckCircleFilled } from '@ant-design/icons';

const Pricing = () => {
  const plans = [
    {
      title: "Boshlang'ich (Starter)",
      price: "99,000",
      period: "oy",
      description: "Yangi boshlayotgan yakka tartibdagi sartaroshxonalar uchun qulay boshqaruv.",
      features: [
        "1 ta faol sartaroshxona filiali",
        "3 tagacha sartarosh xodimlari",
        "Mijozlarni telegram orqali yozib olish",
        "Kundalik xizmatlar va buyurtmalar statistikasi",
        "Standard telegram bot integratsiyasi"
      ],
      isPopular: false,
      buttonText: "Starter bilan boshlash",
      color: "border-gray-200"
    },
    {
      title: "Kengaytirilgan (Pro)",
      price: "199,000",
      period: "oy",
      description: "O'sib borayotgan sartaroshxonalar va studiyalar uchun mukammal yechim.",
      features: [
        "3 tagacha sartaroshxona filiali",
        "Cheksiz sartarosh xodimlar profili",
        "AI tavsiyalar va No-Show xavfini baholash",
        "Real-time buyurtmalar va WebSockets paneli",
        "Premium Telegram Stars to'lov tizimi",
        "Telegram va veb-analitika xabarnomalari"
      ],
      isPopular: true,
      buttonText: "Pro darajaga o'tish",
      color: "border-indigo-500 ring-2 ring-indigo-600 ring-opacity-50"
    },
    {
      title: "Biznes (Enterprise)",
      price: "499,000",
      period: "oy",
      description: "Cheksiz imkoniyatlar va to'liq avtomatlashtirilgan yirik tarmoqlar uchun.",
      features: [
        "Cheksiz sartaroshxona filiallari (Multi-Tenant)",
        "Cheksiz usta xodimlari va ish jadvallari",
        "To'liq avtomatlashtirilgan Trigger/Actions tizimi",
        "Maxsus shaxsiy Telegram Bot",
        "VIP mijozlar segmentatsiyasi va SMS marketing",
        "24/7 ustuvor yordam va shaxsiy menejer"
      ],
      isPopular: false,
      buttonText: "Enterprise ulanish",
      color: "border-gray-200"
    }
  ];

  return (
    <div className="py-12 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl sm:tracking-tight lg:text-6xl">
            Sizning biznesingiz uchun <span className="text-indigo-600">mukammal narxlar</span>
          </h1>
          <p className="max-w-xl mt-5 mx-auto text-xl text-gray-500">
            Filiallar va sartaroshlar soniga mos ravishda eng maqbul tarifni tanlang. Yashirin to'lovlarsiz!
          </p>
        </div>

        {/* Pricing Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch mb-16">
          {plans.map((plan, index) => {
            const cardContent = (
              <Card 
                className={`h-full flex flex-col justify-between shadow-lg hover:shadow-2xl transition-all duration-300 rounded-2xl border-2 ${plan.color}`}
                bodyStyle={{ height: '100%', display: 'flex', flexDirection: 'column', padding: '32px' }}
              >
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.title}</h3>
                  <p className="text-gray-500 text-sm mb-6 min-h-[48px]">{plan.description}</p>
                  
                  <div className="flex items-baseline mb-8">
                    <span className="text-5xl font-extrabold text-gray-900">{plan.price}</span>
                    <span className="text-lg font-medium text-gray-500 ml-2">UZS / {plan.period}</span>
                  </div>

                  <ul className="space-y-4 mb-8">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start">
                        <CheckCircleFilled className="text-indigo-600 mr-3 mt-1 text-base flex-shrink-0" />
                        <span className="text-gray-600 text-base">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="mt-auto">
                  <Button 
                    type={plan.isPopular ? "primary" : "default"}
                    className={`w-full h-12 text-lg font-semibold rounded-xl ${
                      plan.isPopular ? "bg-indigo-600 hover:bg-indigo-500 text-white border-0" : "hover:text-indigo-600 hover:border-indigo-600"
                    }`}
                  >
                    {plan.buttonText}
                  </Button>
                </div>
              </Card>
            );

            return plan.isPopular ? (
              <Badge.Ribbon text="TAVSIYA ETILADI" color="#4f46e5" key={index}>
                {cardContent}
              </Badge.Ribbon>
            ) : (
              <div key={index} className="h-full">
                {cardContent}
              </div>
            );
          })}
        </div>

        {/* Pricing Comparison Info */}
        <div className="bg-white rounded-2xl shadow-md p-8 md:p-12 border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Tez-tez so'raladigan savollar</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Tarifni istalgan paytda o'zgartira olamanmi?</h3>
              <p className="text-gray-600">
                Ha, albatta! Istalgan vaqtda yuqori tarifga o'tishingiz yoki tarifni pasaytirishingiz mumkin. To'lovingiz avtomatik qayta hisoblab chiqiladi.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Telegram Stars to'lov tizimi qanday ishlaydi?</h3>
              <p className="text-gray-600">
                Mijozlaringiz xizmatlarni bron qilish paytida bevosita Telegram bot ichida Telegram Stars orqali to'lov qila oladilar. Ushbu to'lovlar sizning tizimdagi balansingizga avtomatik tarzda 1 Star = 200 UZS kursida qayd etiladi.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Pricing;
