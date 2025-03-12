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
} from "antd";
import { useDispatch } from "react-redux";
import * as XLSX from "xlsx";
import { saveAs } from "file-saver";
import PropTypes from "prop-types";
import { debounce } from "lodash";
import moment from "moment";
import {
  DownloadOutlined,
  SyncOutlined,
  CheckOutlined,
} from "@ant-design/icons";
import {
  fetchRecent,
  getRawMessage,
  processMessage,
} from "../redux/action/action";
import { useRawMessages } from "../hooks/useRawMessages";

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
  const dispatch = useDispatch();

  const { rawMessages, loading, total, error } = useRawMessages();
  const length = rawMessages.length;

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

  const handleProcessMessage = () => {
    dispatch(processMessage())
      .unwrap()
      .then(() => {
        antdMessage.success("Messages processed successfully!");
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
      const allMessages = response?.servey || response?.messages || [];

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
        saveAs(blob, "messages.csv");
      } else if (format === "excel") {
        const ws = XLSX.utils.json_to_sheet(allMessages);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Messages");
        const excelBuffer = XLSX.write(wb, { bookType: "xlsx", type: "array" });
        const blob = new Blob([excelBuffer], {
          type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        });
        saveAs(blob, "messages.xlsx");
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

  const handleFetchRecent = async (e) => {
    e.preventDefault();
    const response = await dispatch(fetchRecent());
    if (response.type === "FETCH_RECENT/fulfilled") {
      antdMessage.success(`${response.payload.total.length} fetched`);
    }
  };

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
        // Convert dates to timestamps for comparison
        const dateA = moment(a.message_date).valueOf();
        const dateB = moment(b.message_date).valueOf();
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
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Button
            type="default"
            icon={<SyncOutlined />}
            onClick={handleFetchRecent}
          >
            Fetch Recent Messages
          </Button>
        </Col>
        {length ? (
          <Col>
            <Space>
              <Button
                type="text"
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
        ) : (
          ""
        )}
      </Row>

      {/* Add Search Input */}
      <Row style={{ marginBottom: 16, justifyContent: "space-evenly" }}>
        <Col span={8}>
          <Search
            placeholder="Search by channel title"
            allowClear
            enterButton="Search"
            onChange={(e) => handleSearch(e.target.value)}
          />
        </Col>
        <Col>
          <RangePicker onChange={handleDateChange} />
        </Col>
      </Row>

      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={rawMessages}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            onChange: (page, pageSize) => {
              setPage(page);
              setPageSize(pageSize);
            },
          }}
          rowKey={(record) => record.message_id || record.id || Math.random()}
          scroll={{ x: true }}
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
