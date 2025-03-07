import React, { useState, useEffect } from "react";
import { Table, Spin, Button } from "antd";
import { useDispatch } from "react-redux";
import { fetchRecent, getRawMessage } from "../redux/action/action";
import { useRawMessages } from "../hooks/useRawMessages";

const RawDataTable = () => {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const dispatch = useDispatch();

  const { rawMessages, loading, total } = useRawMessages();

  useEffect(() => {
    dispatch(getRawMessage({ page, page_size: pageSize }));
  }, [dispatch, page, pageSize]);

  const handleFetchRecent = (e) => {
    e.preventDefault();
    dispatch(fetchRecent()); // Dispatch action to fetch recent messages
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
    },
    { title: "Message", dataIndex: "message", key: "message" },
    {
      title: "Media",
      dataIndex: "media",
      key: "media",
      render: (media) =>
        media ? (
          <a href={media} target="_blank" rel="noopener noreferrer">
            {media}
          </a>
        ) : (
          "N/A"
        ),
    },
  ];

  return (
    <Spin spinning={loading}>
      <Button onClick={handleFetchRecent} style={{ marginBottom: "16px" }}>
        Fetch Recent Messages
      </Button>
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
      />
    </Spin>
  );
};

export default RawDataTable;
