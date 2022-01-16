from struct import unpack, calcsize


class DataStruct:
    fmt = ''
    fields = []

    @classmethod
    def read(cls, file):
        self = cls()
        # buff = file.read()
        buff = file.read(cls.size())
        header = unpack(cls.fmt, buff)
        for i in range(len(cls.fields)):
            setattr(self, cls.fields[i], header[i])
        return self

    @classmethod
    def size(cls):
        return calcsize(cls.fmt)


class FileHeader(DataStruct):
    fmt = '1i1i1i1i'
    fields = ['next_page_addr', 'page_size', 'storage_ver', 'reserved']
    end_marker = 0x7fffffff

    def __init__(self):
        self.next_page_addr = None
        self.page_size = None
        self.storage_ver = None
        self.reserved = None  # // всегда  ? 0x00000000

    @classmethod
    def read(cls, file):
        self = super().read(file)
        self.next_page_addr = self.next_page_addr if self.next_page_addr != cls.end_marker else None
        return self


class BlockHeader(DataStruct):
    fmt = '1c1c8s1c8s1c8s1c1c1c'
    fields = [
        'EOL_0D', 'EOL_0A', 'data_size_hex', 'space1', 'page_size_hex', 'space2', 'next_page_addr_hex', 'space3',
        'EOL2_0D', 'EOL2_0A']

    def __init__(self):
        self.EOL_0D = None
        self.EOL_0A = None
        self.data_size_hex = None  # char[8]
        self.space1 = None
        self.page_size_hex = None
        self.space2 = None
        self.next_page_addr_hex = None
        self.space3 = None
        self.EOL2_0D = None
        self.EOL2_0A = None

    def is_correct(self):
        return int.from_bytes(self.EOL_0D, byteorder="big") == 0x0d \
               and int.from_bytes(self.EOL_0A, byteorder="big") == 0x0a \
               and int.from_bytes(self.space1, byteorder="big") == 0x20 \
               and int.from_bytes(self.space2, byteorder="big") == 0x20 \
               and int.from_bytes(self.space3, byteorder="big") == 0x20 \
               and int.from_bytes(self.EOL2_0D, byteorder="big") == 0x0d \
               and int.from_bytes(self.EOL2_0A, byteorder="big") == 0x0a


# 	static const UINT Size()
# 	
# 		return 8 + 4 + 4 + 4
# 	
# 
# 
# struct stElemAddr
# 
# 	DWORD elem_header_addr
# 	DWORD elem_data_addr
# 	DWORD fffffff //всегда 0x7fffffff ?
# 
# 	static const UINT Size()
# 	
# 		return 4 + 4 + 4
# 	
# 
# 
# 
# struct stElemAddr64
# 
# 	// каждый элемент стал 64 бита
# 	ULONGLONG elem_header_addr
# 	ULONGLONG elem_data_addr
# 	ULONGLONG fffffff //всегда 0xffffffffffffffff ?
# 
# 	static const UINT Size()
# 	
# 		return 8 + 8 + 8
# 	
# 
# 
#


#
# struct stBlockHeader64
# 
# 	EOL_0D
# 	EOL_0A
# 	data_size_hex[16] =  ' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '  // 64 бита теперь
# 	space1
# 	page_size_hex[16] =  ' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '  // 64 бита теперь
# 	space2
# 	next_page_addr_hex[16] =  ' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '  // 64 бита теперь
# 	space3
# 	EOL2_0D
# 	EOL2_0A
# 
# 	stBlockHeader64() :
# 		EOL_0D(0xd), EOL_0A(0xa),
# 		space1(' '), space2(' '), space3(' '),
# 		EOL2_0D(0xd), EOL2_0A(0xa)
# 	
# 		
# 	
# 
# 	static stBlockHeader64 create(ULONGLONG block_data_size, ULONGLONG page_size, ULONGLONG next_page_addr)
# 
# 	static const UINT Size()
# 	
# 		return 1 + 1 + 16 + 1 + 16 + 1 + 16 + 1 + 1 + 1 // 55 теперь
# 	
# 
# 	bool IsCorrect() const
# 	
# 		return EOL_0D == 0x0d
# 			&& EOL_0A == 0x0a
# 			&& space1 == 0x20
# 			&& space2 == 0x20
# 			&& space3 == 0x20
# 			&& EOL2_0D == 0x0d
# 			&& EOL2_0A == 0x0a
# 	
# 

class CV8File:
    header_offset = 0
    class_file_header = FileHeader
    class_block_header = BlockHeader

    @classmethod
    def is_v8_file(cls, file):
        file.seek(cls.header_offset, 0)
        file_header = cls.class_file_header.read(file)
        block_header = cls.class_block_header.read(file)
        return block_header.is_correct()

    def parse(self, file, dest_dir):
        pass
        ret = self.unpack_to_directory_no_load(dest_dir, file, filter)
        #
        # if (ret == V8UNPACK_NOT_V8_FILE)
        #     std::cerr << "Parse. `" << filename_in << "` is not V8 file!" << std::endl
        #     return ret

    @classmethod
    def unpack_to_directory_no_load(cls, directory: str, file, filter: list, bool_inflate: bool,
                                    unpack_when_need: bool):
        pass
        #
        # boost::filesystem::path p_dir(directory)
        #
        # if (!boost::filesystem::exists(p_dir))
        #     if (!boost::filesystem::create_directory(directory))
        #         std::cerr << "UnpackToDirectoryNoLoad. Error in creating directory!" << std::endl
        #         return ret
        #
        #
        #
        # stFileHeader FileHeader
        # file.read((char*)&FileHeader, sizeof(FileHeader))
        #
        # stBlockHeader BlockHeader
        # stBlockHeader *pBlockHeader = &BlockHeader
        #
        # file.read((char*)&BlockHeader, sizeof(BlockHeader))
        #
        # UINT ElemsAddrsSize
        # stElemAddr *pElemsAddrs = nullptr
        # ReadBlockData(file, pBlockHeader, (char*&)pElemsAddrs, &ElemsAddrsSize)
        #
        # unsigned int ElemsNum = ElemsAddrsSize / stElemAddr::Size()
        #
        # for (UINT i = 0 i < ElemsNum i++)
        #
        #     if (pElemsAddrs[i].fffffff != V8_FF_SIGNATURE)
        #         ElemsNum = i
        #         break
        #
        #
        #     file.seekg(pElemsAddrs[i].elem_header_addr, std::ios_base::beg)
        #     file.read((char*)&BlockHeader, sizeof(BlockHeader))
        #
        #     if (!pBlockHeader->IsCorrect())
        #         ret = V8UNPACK_HEADER_ELEM_NOT_CORRECT
        #         break
        #
        #
        #     CV8Elem elem
        #     ReadBlockData(file, pBlockHeader, elem.pHeader, &elem.HeaderSize)
        #
        #     string ElemName = elem.GetName()
        #
        #     if (!NameInFilter(ElemName, filter))
        #         continue
        #
        #
        #     boost::filesystem::path elem_path(p_dir / ElemName)
        #     elem_path = boost::filesystem::absolute(elem_path)
        #
        #     //080228 Блока данных может не быть, тогда адрес блока данных равен 0x7fffffff
        #     if (pElemsAddrs[i].elem_data_addr != V8_FF_SIGNATURE)
        #         file.seekg(pElemsAddrs[i].elem_data_addr, std::ios_base::beg)
        #         SmartUnpack(file, boolInflate/* && IsDataPacked*/, elem_path)
        #      else
        #         // TODO: Зачем это нужно??
        #         //ReadBlockData(file, nullptr, o_tmp, &elem.DataSize)
        #
        #
        #     delete [] elem.pHeader
        #
        #   // for i = ..ElemsNum
        #
        # delete [] pElemsAddrs
        #
        # return ret
