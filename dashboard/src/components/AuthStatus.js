import React from "react";
import { Badge, Tag, Tooltip } from "antd";
import {
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from "@ant-design/icons";

const AuthStatus = ({ authenticated, loading }) => {
  if (loading) {
    return <Tag color="processing">Checking auth...</Tag>;
  }

  return authenticated ? (
    <Tooltip title="Telegram authenticated">
      <Badge status="success" text="Authenticated" />
    </Tooltip>
  ) : (
    <Tooltip title="Telegram authentication required">
      <Badge status="error" text="Not Authenticated" />
    </Tooltip>
  );
};

export default AuthStatus;
