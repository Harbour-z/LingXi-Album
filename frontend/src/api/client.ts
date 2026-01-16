import axios, { AxiosInstance, AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios';

// 定义API响应的基本结构
export interface ApiResponse<T = any> {
    status: 'success' | 'error';
    message: string;
    data?: T;
    // 兼容其他可能的字段
    [key: string]: any;
}

const client: AxiosInstance = axios.create({
    baseURL: '/api/v1',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// 请求拦截器
client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        // 可以在这里添加 token
        // const token = localStorage.getItem('token');
        // if (token) {
        //     config.headers.Authorization = `Bearer ${token}`;
        // }
        return config;
    },
    (error: AxiosError) => {
        return Promise.reject(error);
    }
);

// 响应拦截器
client.interceptors.response.use(
    (response: AxiosResponse) => {
        // 直接返回 response.data，这样调用方拿到的是 ApiResponse
        return response.data;
    },
    (error: AxiosError) => {
        const message = (error.response?.data as any)?.message || error.message || '请求失败';
        console.error('API Error:', message);
        // 这里可以触发全局的错误提示，但为了解耦，建议在调用层处理或使用 EventBus
        return Promise.reject(new Error(message));
    }
);

export default client;
