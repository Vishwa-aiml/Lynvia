import apiClient from '../client';

export const paymentService = {
  createPayment: async (projectId: string) => {
    return apiClient.post(`/projects/${projectId}/payments`);
  },

  verifyPayment: async (paymentId: string, data: { razorpay_order_id: string, razorpay_payment_id: string, razorpay_signature: string }) => {
    return apiClient.post(`/payments/${paymentId}/verify`, data);
  }
};
