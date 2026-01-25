import React, { useState } from 'react';
import { Modal, Upload, message, Button, Spin } from 'antd';
import { InboxOutlined, SearchOutlined, DeleteOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd/es/upload/interface';
import { searchByUploadedImage } from '../../api/search';
import { useNavigate } from 'react-router-dom';

const { Dragger } = Upload;

interface ImageSearchModalProps {
    open: boolean;
    onCancel: () => void;
    topK?: number;
}

export const ImageSearchModal: React.FC<ImageSearchModalProps> = ({
    open,
    onCancel,
    topK = 10
}) => {
    const [fileList, setFileList] = useState<UploadFile[]>([]);
    const [uploading, setUploading] = useState(false);
    const [previewImage, setPreviewImage] = useState<string>('');
    const navigate = useNavigate();

    const handleUpload = async () => {
        if (fileList.length === 0) {
            message.warning('请先选择一张图片');
            return;
        }

        const file = fileList[0].originFileObj as File;
        setUploading(true);

        try {
            const result = await searchByUploadedImage(file, topK);
            
            if (result.status === 'success') {
                message.success('搜索完成');
                onCancel();
                // Navigate to gallery with results
                navigate('/gallery', { 
                    state: { 
                        searchResults: result.data, 
                        searchType: 'image',
                        searchQuery: file.name,
                        total: result.total
                    } 
                });
            } else {
                message.error(result.message || '搜索失败');
            }
        } catch (error: unknown) {
            const errorMessage = error instanceof Error ? error.message : '搜索过程中发生错误';
            message.error(errorMessage);
        } finally {
            setUploading(false);
        }
    };

    const props: UploadProps = {
        onRemove: () => {
            setFileList([]);
            setPreviewImage('');
        },
        beforeUpload: (file) => {
            const isImage = file.type.startsWith('image/');
            if (!isImage) {
                message.error('只能上传图片文件!');
                return Upload.LIST_IGNORE;
            }
            
            const isLt10M = file.size / 1024 / 1024 < 10;
            if (!isLt10M) {
                message.error('图片必须小于 10MB!');
                return Upload.LIST_IGNORE;
            }

            setFileList([
                {
                    uid: file.uid,
                    name: file.name,
                    status: 'done',
                    originFileObj: file,
                },
            ]);
            
            // Create preview
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => setPreviewImage(reader.result as string);
            
            return false; // Prevent automatic upload
        },
        fileList,
        maxCount: 1,
        showUploadList: false, // Custom preview
    };

    return (
        <Modal
            title="以图搜图"
            open={open}
            onCancel={onCancel}
            footer={[
                <Button key="cancel" onClick={onCancel} disabled={uploading}>
                    取消
                </Button>,
                <Button
                    key="search"
                    type="primary"
                    loading={uploading}
                    onClick={handleUpload}
                    disabled={fileList.length === 0}
                    icon={<SearchOutlined />}
                >
                    开始搜索
                </Button>,
            ]}
            width={600}
        >
            <div style={{ marginTop: 16, marginBottom: 16 }}>
                {previewImage ? (
                    <div style={{ position: 'relative', textAlign: 'center', padding: '20px', border: '1px dashed #d9d9d9', borderRadius: '8px' }}>
                        <img 
                            src={previewImage} 
                            alt="Preview" 
                            style={{ maxWidth: '100%', maxHeight: '300px', objectFit: 'contain' }} 
                        />
                        <Button 
                            type="text" 
                            danger 
                            icon={<DeleteOutlined />} 
                            style={{ position: 'absolute', top: 8, right: 8, background: 'rgba(255,255,255,0.8)' }}
                            onClick={() => {
                                setFileList([]);
                                setPreviewImage('');
                            }}
                        />
                    </div>
                ) : (
                    <Dragger {...props} style={{ padding: '40px 0' }}>
                        <p className="ant-upload-drag-icon">
                            <InboxOutlined />
                        </p>
                        <p className="ant-upload-text">点击或拖拽图片到此处上传</p>
                        <p className="ant-upload-hint">
                            支持 JPG, PNG, WebP 等格式，最大 10MB
                        </p>
                    </Dragger>
                )}
            </div>
            
            {uploading && (
                <div style={{ textAlign: 'center', margin: '20px 0' }}>
                    <Spin tip="正在分析图片并搜索..." />
                </div>
            )}
        </Modal>
    );
};
