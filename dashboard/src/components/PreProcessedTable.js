import React, { useState, useEffect } from "react";
import {
  Table,
  Spin,
  Button,
  Dropdown,
  Menu,
  message as antdMessage,
  Row,
  Col,
  Layout,
  Typography,
} from "antd";
import { useDispatch } from "react-redux";
import { getMessage } from "../redux/action/action";
import { useMessages } from "../hooks/useMessages";
import { DownloadOutlined } from "@ant-design/icons";
import * as XLSX from "xlsx";
import { saveAs } from "file-saver";
import PropTypes from "prop-types";

const { Content } = Layout;
const { Title } = Typography;

const PreProcessedTable = () => {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [exporting, setExporting] = useState(false);
  const dispatch = useDispatch();
  const { messages, loading, total, error } = useMessages();

  useEffect(() => {
    dispatch(getMessage({ page, page_size: pageSize }));
  }, [dispatch, page, pageSize]);

  const exportData = async (format) => {
    setExporting(true);
    try {
      const response = await dispatch(
        getMessage({ page: 1, page_size: total })
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

  const columns = [
    {
      title: "Channel Name",
      dataIndex: "channel_title",
      key: "channel_title",
    },
    { title: "Message Id", dataIndex: "message_id", key: "message_id" },
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
    {
      title: "Emoji",
      dataIndex: "emoji",
      key: "emoji",
      render: (emoji) => emoji || "no emoji",
    },
    {
      title: "YouTube",
      dataIndex: "youtube",
      key: "youtube",
      render: (youtube) => {
        if (!youtube || youtube === "no youtube" || youtube === "{}")
          return "No YouTube";

        let youtubeLinks = [];

        if (typeof youtube === "string") {
          // Remove `('` and `',)` brackets and split the links
          youtube = youtube.replace(/[\(\)']/g, "").trim();
          youtubeLinks = youtube.split(",").map((link) => link.trim());
        } else if (Array.isArray(youtube)) {
          youtubeLinks = youtube.filter(
            (link) => link && link !== "no youtube"
          );
        }

        return youtubeLinks.length ? (
          <ul style={{ paddingLeft: "20px" }}>
            {youtubeLinks.map((link, index) => (
              <li key={index} style={{ listStyle: "none" }}>
                <a href={link} target="_blank" rel="noopener noreferrer">
                  ▶
                </a>
              </li>
            ))}
          </ul>
        ) : (
          "No YouTube"
        );
      },
    },
    {
      title: "Phone",
      dataIndex: "phone",
      key: "phone",
      render: (phone) => {
        if (!phone || phone === "no phone" || phone === "{}") return "No Phone";

        let phoneNumbers = [];

        if (typeof phone === "string") {
          // Remove `{}` brackets and split the numbers by comma
          phone = phone.replace(/[{}]/g, "").trim();
          phoneNumbers = phone.split(",").map((num) => num.trim());
        } else if (Array.isArray(phone)) {
          phoneNumbers = phone.filter((num) => num && num !== "no phone");
        } else if (typeof phone === "number") {
          phoneNumbers = [phone.toString()];
        }

        return phoneNumbers.length ? (
          <ul style={{ paddingLeft: "20px" }}>
            {phoneNumbers.map((num, index) => (
              <li key={index} style={{ listStyle: "none" }}>
                📞{" "}
                <a href={`tel:${num}`} style={{ textDecoration: "none" }}>
                  {num}
                </a>
              </li>
            ))}
          </ul>
        ) : (
          "No Phone"
        );
      },
    },
    {
      title: "Message Date",
      dataIndex: "message_date",
      key: "message_date",
      render: (message_date) =>
        message_date ? new Date(message_date).toLocaleString() : "N/A",
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
      <Row justify="end" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Dropdown overlay={menu} trigger={["click"]}>
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              loading={exporting}
            >
              Export
            </Button>
          </Dropdown>
        </Col>
      </Row>
      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={messages}
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
          rowKey={(record) => record.id || record.message_id || Math.random()}
          scroll={{ x: true }} // Make table horizontally scrollable
          loading={loading || exporting}
        />
      </Spin>
    </Content>
  );
};

PreProcessedTable.propTypes = {
  messages: PropTypes.array,
  loading: PropTypes.bool,
  total: PropTypes.number,
  error: PropTypes.string,
};

export default PreProcessedTable;
