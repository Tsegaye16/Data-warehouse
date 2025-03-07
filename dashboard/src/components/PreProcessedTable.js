import React, { useState, useEffect } from "react";
import { Table, Spin } from "antd";
import { useDispatch } from "react-redux";
import { getMessage } from "../redux/action/action";
import { useMessages } from "../hooks/useMessages";

const PreProcessedTable = () => {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const dispatch = useDispatch();

  const { messages, loading, total } = useMessages();

  useEffect(() => {
    dispatch(getMessage({ page, page_size: pageSize }));
  }, [dispatch, page, pageSize]);

  const columns = [
    {
      title: "Channel Title",
      dataIndex: "channel_title",
      key: "channel_title",
    },
    {
      title: "Message Id",
      dataIndex: "message_id",
      key: "message_id",
    },
    { title: "Message", dataIndex: "message", key: "message" },
    {
      title: "Media path",
      dataIndex: "media_path",
      key: "media_path",
      render: (media) =>
        media ? (
          <a href={media} target="_blank" rel="noopener noreferrer">
            {media}
          </a>
        ) : (
          "N/A"
        ),
    },
    {
      title: "Emoji",
      dataIndex: "emoji",
      key: "emoji",
      render: (emoji) => emoji || "N/A",
    },
    {
      title: "YouTube",
      dataIndex: "youtube",
      key: "youtube",
      render: (youtube) => youtube || "N/A",
    },
    {
      title: "Phone",
      dataIndex: "phone",
      key: "phone",
      render: (phone) => phone || "N/A",
    },
    {
      title: "Message Date",
      dataIndex: "message_date",
      key: "message_date",
      render: (message_date) =>
        message_date ? new Date(message_date).toLocaleString() : "N/A",
    },
  ];

  return (
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
      />
    </Spin>
  );
};

export default PreProcessedTable;
