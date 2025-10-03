import React, { useState, useEffect } from "react";
import {
  Modal,
  Form,
  Input,
  Button,
  Alert,
  Steps,
  Typography,
  Space,
} from "antd";
import {
  PhoneOutlined,
  LockOutlined,
  SecurityScanOutlined,
} from "@ant-design/icons";

const { Step } = Steps;
const { Text } = Typography;

const TelegramAuthModal = ({ visible, onCancel, onAuthenticate }) => {
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [authData, setAuthData] = useState({});

  useEffect(() => {
    if (!visible) {
      // Reset form when modal closes
      form.resetFields();
      setCurrentStep(0);
      setError("");
      setAuthData({});
    }
  }, [visible, form]);

  const handleStep1 = async (values) => {
    setLoading(true);
    setError("");

    try {
      const response = await onAuthenticate({
        phone: values.phone,
        password: values.password || null,
      });

      if (response.status === "success") {
        setAuthData({ phone: values.phone, password: values.password });
        setCurrentStep(1);
      } else if (response.status === "code_required") {
        setAuthData({ phone: values.phone, password: values.password });
        setCurrentStep(1);
      } else {
        setError(response.message || "Authentication failed");
      }
    } catch (err) {
      setError(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  const handleStep2 = async (values) => {
    setLoading(true);
    setError("");

    try {
      const response = await onAuthenticate({
        ...authData,
        code: values.code,
      });

      if (response.status === "success") {
        onCancel(); // Close modal on success
      } else {
        setError(response.message || "Verification failed");
      }
    } catch (err) {
      setError(err.message || "Verification failed");
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    {
      title: "Phone & Password",
      content: (
        <Form form={form} layout="vertical" onFinish={handleStep1}>
          <Form.Item
            name="phone"
            label="Phone Number"
            rules={[
              { required: true, message: "Please input your phone number!" },
              {
                pattern: /^\+?[1-9]\d{1,14}$/,
                message: "Please enter a valid phone number!",
              },
            ]}
          >
            <Input
              prefix={<PhoneOutlined />}
              placeholder="+1234567890"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            label="2FA Password (if enabled)"
            help="Leave empty if you don't have two-factor authentication"
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Optional"
              size="large"
            />
          </Form.Item>

          {error && <Alert message={error} type="error" showIcon />}

          <Form.Item style={{ marginTop: 16, marginBottom: 0 }}>
            <Button type="primary" htmlType="submit" loading={loading} block>
              Send Code
            </Button>
          </Form.Item>
        </Form>
      ),
    },
    {
      title: "Verification Code",
      content: (
        <Form layout="vertical" onFinish={handleStep2}>
          <Space direction="vertical" size="middle" style={{ width: "100%" }}>
            <Text>
              We've sent a verification code to your Telegram account. Please
              enter it below:
            </Text>

            <Form.Item
              name="code"
              label="Verification Code"
              rules={[
                {
                  required: true,
                  message: "Please input the verification code!",
                },
                {
                  pattern: /^\d+$/,
                  message: "Please enter a valid numeric code!",
                },
              ]}
            >
              <Input
                prefix={<SecurityScanOutlined />}
                placeholder="123456"
                size="large"
                maxLength={6}
              />
            </Form.Item>

            {error && <Alert message={error} type="error" showIcon />}

            <Space>
              <Button onClick={() => setCurrentStep(0)} disabled={loading}>
                Back
              </Button>
              <Button type="primary" htmlType="submit" loading={loading}>
                Verify & Authenticate
              </Button>
            </Space>
          </Space>
        </Form>
      ),
    },
  ];

  return (
    <Modal
      title="Telegram Authentication"
      open={visible}
      onCancel={onCancel}
      footer={null}
      width={500}
      destroyOnClose
    >
      <Steps current={currentStep} size="small" style={{ marginBottom: 24 }}>
        {steps.map((step) => (
          <Step key={step.title} title={step.title} />
        ))}
      </Steps>

      {steps[currentStep].content}
    </Modal>
  );
};

export default TelegramAuthModal;
