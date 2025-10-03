import React, { useState, useEffect, useMemo } from "react";
import {
  Table,
  Menu,
  Dropdown,
  Spin,
  Button,
  Layout,
  Row,
  Col,
  Space,
  Typography,
  message as antdMessage,
  Input,
  DatePicker,
  Alert,
} from "antd";
import { useDispatch, useSelector } from "react-redux";
import * as XLSX from "xlsx";
import { saveAs } from "file-saver";
import PropTypes from "prop-types";
import { debounce } from "lodash";
import moment from "moment";
import {
  DownloadOutlined,
  SyncOutlined,
  CheckOutlined,
  UserOutlined,
} from "@ant-design/icons";
import {
  fetchRecent,
  getRawMessage,
  processMessage,
} from "../redux/action/action";
import { useRawMessages } from "../hooks/useRawMessages";
import TelegramAuthModal from "./TelegramAuthModal";
import AuthStatus from "./AuthStatus";

const { Content } = Layout;
const { Title } = Typography;
const { Search } = Input;
const { RangePicker } = DatePicker;

const RawDataTable = () => {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [exporting, setExporting] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [dateRange, setDateRange] = useState([null, null]);
  const [channelInput, setChannelInput] = useState("");
  const [authModalVisible, setAuthModalVisible] = useState(false);
  const [authStatus, setAuthStatus] = useState({
    authenticated: false,
    loading: true,
  });
  const [fetchLoading, setFetchLoading] = useState(false);

  const dispatch = useDispatch();
  const { rawMessages, loading, total, error } = useRawMessages();
  const length = rawMessages.length;

  // Check authentication status on component mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    setAuthStatus((prev) => ({ ...prev, loading: true }));
    try {
      const response = await fetch("http://127.0.0.1:8000/auth/status");
      const data = await response.json();
      setAuthStatus({ authenticated: data.authenticated, loading: false });
    } catch (error) {
      setAuthStatus({
        authenticated: false,
        loading: false,
        error: error.message,
      });
    }
  };

  // Debounced search function (memoized)
  const handleSearch = useMemo(
    () =>
      debounce((value) => {
        setSearchTerm(value);
        setPage(1);
      }, 300),
    []
  );

  useEffect(() => {
    dispatch(
      getRawMessage({
        page,
        page_size: pageSize,
        channel_name: searchTerm,
        start_date: dateRange[0] ? dateRange[0].format("YYYY-MM-DD") : null,
        end_date: dateRange[1] ? dateRange[1].format("YYYY-MM-DD") : null,
      })
    );
  }, [dispatch, page, pageSize, searchTerm, dateRange]);

  const handleDateChange = (dates) => {
    setDateRange(dates ? dates : [null, null]);
    setPage(1);
  };

  const handleAuthenticate = async (authData) => {
    try {
      const response = await fetch("http://127.0.0.1:8000/auth/telegram", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(authData),
      });

      const result = await response.json();

      if (result.status === "success") {
        antdMessage.success("Authenticated successfully!");
        setAuthStatus({ authenticated: true, loading: false });
        setAuthModalVisible(false);
      }

      return result;
    } catch (error) {
      throw new Error(error.message || "Authentication failed");
    }
  };

  const handleFetchRecent = async (e) => {
    // Check authentication before fetching
    if (!authStatus.authenticated) {
      antdMessage.warning("Please authenticate with Telegram first!");
      setAuthModalVisible(true);
      return;
    }

    const channels = channelInput
      .split("\n")
      .filter((channel) => channel.trim());

    // if (channels.length === 0) {
    //   antdMessage.warning("Please enter at least one channel URL");
    //   return;
    // }

    setFetchLoading(true);
    try {
      const response = await dispatch(fetchRecent({ channels })).unwrap();

      // Handle the response properly based on your API structure
      if (response.messages || response.total >= 0) {
        antdMessage.success(
          `Successfully fetched ${
            response.total || response.messages?.length || 0
          } messages!`
        );

        // Refresh the raw messages list
        dispatch(
          getRawMessage({
            page: 1,
            page_size: pageSize,
            channel_name: searchTerm,
          })
        );

        setChannelInput("");
      } else {
        antdMessage.error("Failed to fetch messages. Please try again.");
      }
    } catch (error) {
      console.error("Fetch error:", error);

      // Handle authentication errors
      if (
        error?.includes("authentication required") ||
        error?.includes("401")
      ) {
        antdMessage.error(
          "Authentication required. Please authenticate again."
        );
        setAuthStatus({ authenticated: false, loading: false });
        setAuthModalVisible(true);
      } else if (error?.message) {
        antdMessage.error(error.message);
      } else {
        antdMessage.error("Failed to fetch recent messages");
      }
    } finally {
      setFetchLoading(false);
    }
  };

  const handleProcessMessage = () => {
    dispatch(processMessage())
      .unwrap()
      .then(() => {
        antdMessage.success("Messages processed successfully!");
        // Refresh both tables after processing
        dispatch(
          getRawMessage({
            page: 1,
            page_size: pageSize,
            channel_name: searchTerm,
          })
        );
      })
      .catch((error) => {
        antdMessage.error(error || "Failed to process messages");
      });
  };

  const exportData = async (format) => {
    setExporting(true);
    try {
      const response = await dispatch(
        getRawMessage({ page: 1, page_size: total, channel_name: searchTerm })
      ).unwrap();
      const allMessages = response?.messages || [];

      if (!allMessages.length) {
        antdMessage.error("No data available for export!");
        setExporting(false);
        return;
      }

      if (format === "csv") {
        const csvContent = [
          Object.keys(allMessages[0]).join(","), // Headers
          ...allMessages.map((row) =>
            Object.values(row)
              .map((value) => `"${value}"`)
              .join(",")
          ),
        ].join("\n");

        const blob = new Blob([csvContent], {
          type: "text/csv;charset=utf-8;",
        });
        saveAs(blob, "raw_messages.csv");
      } else if (format === "excel") {
        const ws = XLSX.utils.json_to_sheet(allMessages);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Raw Messages");
        const excelBuffer = XLSX.write(wb, { bookType: "xlsx", type: "array" });
        const blob = new Blob([excelBuffer], {
          type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        });
        saveAs(blob, "raw_messages.xlsx");
      }

      antdMessage.success(`Exported data as ${format.toUpperCase()}`);
    } catch (error) {
      antdMessage.error("Failed to fetch data for export!");
    }
    setExporting(false);
  };

  const menu = (
    <Menu>
      <Menu.Item key="csv" onClick={() => exportData("csv")}>
        Export as CSV
      </Menu.Item>
      <Menu.Item key="excel" onClick={() => exportData("excel")}>
        Export as Excel
      </Menu.Item>
    </Menu>
  );

  const columns = [
    { title: "Channel Name", dataIndex: "channel_name", key: "channel_name" },
    { title: "Message ID", dataIndex: "message_id", key: "message_id" },
    { title: "Sender", dataIndex: "sender", key: "sender" },
    {
      title: "Timestamp",
      dataIndex: "timestamp",
      key: "timestamp",
      render: (timestamp) =>
        timestamp ? new Date(timestamp).toLocaleString() : "N/A",
      sorter: (a, b) => {
        const dateA = moment(a.timestamp).valueOf();
        const dateB = moment(b.timestamp).valueOf();
        return dateA - dateB;
      },
    },
    { title: "Message", dataIndex: "message", key: "message" },
    {
      title: "Media Path",
      dataIndex: "media_path",
      key: "media_path",
      render: (media) =>
        media && media.toLowerCase() !== "no media" ? (
          <a href={media} target="_blank" rel="noopener noreferrer">
            {media}
          </a>
        ) : (
          "no media"
        ),
    },
  ];

  if (error) {
    return (
      <Content style={{ padding: "24px", textAlign: "center" }}>
        <Title level={4} type="danger">
          Error: {error}
        </Title>
      </Content>
    );
  }

  return (
    <Content style={{ padding: "24px" }}>
      <TelegramAuthModal
        visible={authModalVisible}
        onCancel={() => setAuthModalVisible(false)}
        onAuthenticate={handleAuthenticate}
      />

      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Space>
            <Button
              type="primary"
              icon={<SyncOutlined />}
              onClick={handleFetchRecent}
              loading={fetchLoading}
              disabled={!authStatus.authenticated}
            >
              Fetch Recent Messages
            </Button>

            {/* Show authenticate button only when NOT authenticated */}
            {!authStatus.authenticated && !authStatus.loading && (
              <Button
                type="dashed"
                icon={<UserOutlined />}
                onClick={() => setAuthModalVisible(true)}
              >
                Authenticate Telegram
              </Button>
            )}

            <AuthStatus
              authenticated={authStatus.authenticated}
              loading={authStatus.loading}
            />
          </Space>
        </Col>
        {length > 0 && (
          <Col>
            <Space>
              <Button
                type="primary"
                icon={<CheckOutlined />}
                onClick={handleProcessMessage}
              >
                Process Messages
              </Button>
              <Dropdown overlay={menu} trigger={["click"]}>
                <Button
                  type="default"
                  icon={<DownloadOutlined />}
                  loading={exporting}
                >
                  Export
                </Button>
              </Dropdown>
            </Space>
          </Col>
        )}
      </Row>

      {!authStatus.authenticated && !authStatus.loading && (
        <Alert
          message="Telegram Authentication Required"
          description="You need to authenticate with Telegram to fetch recent messages. Click the 'Authenticate Telegram' button to proceed."
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {authStatus.authenticated && (
        <Alert
          message="Telegram Authenticated"
          description="You are now authenticated with Telegram. You can fetch messages from channels."
          type="success"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Row style={{ marginBottom: 16 }}>
        <Col span={24}>
          <Input.TextArea
            rows={4}
            placeholder="Enter Telegram channel URLs (one per line)
Example:
https://t.me/DoctorsET
https://t.me/CheMed123
https://t.me/yetenaweg"
            value={channelInput}
            onChange={(e) => setChannelInput(e.target.value)}
            style={{ marginBottom: 8 }}
          />
          <Typography.Text type="secondary">
            Enter one channel URL per line. Leave empty to use default channels.
          </Typography.Text>
        </Col>
      </Row>

      <Row style={{ marginBottom: 16, justifyContent: "space-between" }}>
        <Col span={12}>
          <Search
            placeholder="Search by channel name"
            allowClear
            enterButton="Search"
            size="large"
            onChange={(e) => handleSearch(e.target.value)}
          />
        </Col>
        <Col>
          <RangePicker onChange={handleDateChange} size="large" />
        </Col>
      </Row>

      <Spin spinning={loading || fetchLoading}>
        <Table
          columns={columns}
          dataSource={rawMessages}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} items`,
            onChange: (page, pageSize) => {
              setPage(page);
              setPageSize(pageSize);
            },
          }}
          rowKey={(record) =>
            `${record.message_id}_${record.channel_name}_${Math.random()}`
          }
          scroll={{ x: true }}
          size="middle"
        />
      </Spin>
    </Content>
  );
};

RawDataTable.propTypes = {
  messages: PropTypes.array,
  loading: PropTypes.bool,
  total: PropTypes.number,
  error: PropTypes.string,
};

export default RawDataTable;
