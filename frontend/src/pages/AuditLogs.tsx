import React from 'react';
import { Typography, Box } from '@mui/material';

const AuditLogs: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4">Audit Logs</Typography>
      <Typography variant="body1">This page will show audit logs and activity history.</Typography>
    </Box>
  );
};

export default AuditLogs;